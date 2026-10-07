#!/usr/bin/env python3
"""Build the SQLD Concept Structure DAG + Learning DAG from the workbook (source of truth).

Default input: SQLD_knowledge_graph_v0_5_with_content.xlsx

Pipeline
  1. read the workbook (16–20 graph sheets, 10/11/13 evidence, 21–26 learning content)
  2. normalise nodes (Node ID is canonical), evidence, legacy status
  3. Concept Structure DAG = 17 BELONGS_TO + IS_A (+ inferred grouping for curated nodes)
  4. Learning DAG = explicit prerequisites (21.Prerequisites concept tokens ∪ 17 REQUIRES/PRECEDES/
     ENABLES/EXPLAINS) + curated inferred edges that the explicit edges do not already imply
  5. cycle check on both candidate graphs -> cycle_report.json (no edge is silently deleted;
     excluded candidates are kept with the review reason)
  6. attach learning content from 21–25 by Node ID; keep v0.4 curated notes only as labelled
     supplementary material
  7. visibility / support / priority / display tiers, write data/*.json + web/data.js,
     then run validate_graph.validate()

Usage:  python3 scripts/build_learning_graph.py [--xlsx path]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent  # Obsidian vault root (Concepts/, Questions/) — read only
sys.path.insert(0, str(ROOT / "scripts"))

from curation import comparisons as cmp_mod  # noqa: E402
from curation import content as content_mod  # noqa: E402
from curation import dialects as dialect_mod  # noqa: E402
from curation import prerequisites as prereq_mod  # noqa: E402
from curation import structure as st  # noqa: E402
import validate_graph  # noqa: E402

DATA = ROOT / "data"
WEB = ROOT / "web"
DEFAULT_XLSX = ROOT / "SQLD_knowledge_graph_v0_5_with_content.xlsx"

STRUCT_TYPES = {"ROOT", "DOMAIN", "CLUSTER"}
CONCEPT_TYPES = {"CONCEPT", "SYNTAX", "FUNCTION", "RULE"}
SUPPLEMENTARY_LABEL = "curated-v0.4 (Claude 작성 보조 노트 · 원본 아님 · 검토 필요)"

# Name references in 25_Dialect_Notes that have no Concept node of their own.
DIALECT_NAME_ALIASES = {
    "ISNULL": ("NVL", "ISNULL은 SQL Server의 NULL 대체 함수로 별도 Concept 노드가 없어 Oracle 대응 함수 NVL에 연결"),
}


# ---------------------------------------------------------------------------
# 1. Workbook
# ---------------------------------------------------------------------------
TABULAR_SHEETS = [
    "02_Concept_Master", "03_Round_Concepts", "04_Mindmap_Gaps", "10_Current_Evidence", "11_Legacy_Only",
    "13_Current_Mindmap_Gaps", "16_KG_Nodes", "17_KG_Edges", "18_Learning_DAG", "19_Study_Outline_v2",
    "20_Hubs_Rules", "21_Concept_Content", "22_Rules_And_Traps", "23_Comparisons", "24_SQL_Examples",
    "25_Dialect_Notes",
]


def read_workbook(path: Path) -> dict[str, list[dict]]:
    import warnings

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    missing = [n for n in TABULAR_SHEETS + ["26_Content_Coverage"] if n not in wb.sheetnames]
    if missing:
        raise SystemExit(f"workbook is missing sheets: {missing}")
    sheets = {}
    for name in TABULAR_SHEETS:
        rows = list(wb[name].iter_rows(values_only=True))
        header = [str(h).strip() if h is not None else f"col{k}" for k, h in enumerate(rows[0])]
        out = []
        for r in rows[1:]:
            if r is None or all(v is None for v in r):
                continue
            out.append({header[k]: (r[k] if k < len(r) else None) for k in range(len(header))})
        sheets[name] = out
    # 26 is a KPI sheet (label/value pairs), not a table
    kpi = {}
    for r in wb["26_Content_Coverage"].iter_rows(values_only=True):
        for a, b in ((0, 1), (3, 4)):
            if len(r) > b and r[a] is not None and isinstance(r[b], (int, float)):
                kpi[str(r[a]).strip()] = int(r[b])
    sheets["26_Content_Coverage"] = kpi
    wb.close()
    return sheets


def s(v) -> str:
    return "" if v is None else str(v).strip()


def i(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def parse_rounds(v) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", s(v))]


def split_names(v) -> list[str]:
    """Comma-separated concept-name lists. Never split on '/', names such as 'PL/SQL' contain it."""
    return [t.strip() for t in s(v).replace("\n", ",").split(",") if t.strip()]


_JOSA = {"은(는)": ("은", "는"), "을(를)": ("을", "를"), "이(가)": ("이", "가"), "과(와)": ("과", "와"),
         "와(과)": ("과", "와"), "으로(로)": ("으로", "로")}


def josa(text: str) -> str:
    """Pick the Korean particle after a Hangul syllable ('NULL 비교은(는)' -> 'NULL 비교는').
    After a non-Hangul character (e.g. 'RANK은(는)') both forms are kept."""
    def fix(m):
        prev, token = m.group(1), m.group(2)
        code = ord(prev) - 0xAC00
        if not 0 <= code <= 11171:
            return m.group(0)
        has_final = code % 28 != 0
        with_final, without = _JOSA[token]
        if token == "으로(로)" and code % 28 == 8:  # ㄹ 받침 -> 로
            return prev + "로"
        return prev + (with_final if has_final else without)
    return re.sub(r"(.)(은\(는\)|을\(를\)|이\(가\)|과\(와\)|와\(과\)|으로\(로\))", fix, text)


def stage_num(label: str):
    """'Stage 3' -> 3, 'Legacy'/'Stage 99' -> 'L', '전체' -> None."""
    label = s(label)
    if label in ("Legacy", "Stage 99"):
        return "L"
    m = re.match(r"Stage\s*(\d+)$", label)
    return int(m.group(1)) if m else None


def stage_order(stage) -> int:
    return 10 if stage == "L" else int(stage)


def cycles_of(g: nx.DiGraph, limit: int = 50) -> list[list[str]]:
    if nx.is_directed_acyclic_graph(g):
        return []
    return sorted(nx.simple_cycles(g), key=len)[:limit]


# ---------------------------------------------------------------------------
# 2. Build
# ---------------------------------------------------------------------------
def build(xlsx: Path) -> dict:
    sh = read_workbook(xlsx)
    notes: list[str] = []
    broken_refs: list[dict] = []

    # ---- 16_KG_Nodes -------------------------------------------------------
    raw_nodes = {s(r["Node ID"]): r for r in sh["16_KG_Nodes"]}
    if len(raw_nodes) != len(sh["16_KG_Nodes"]):
        raise SystemExit("duplicate Node ID in 16_KG_Nodes")
    domains, clusters, nodes = {}, {}, {}
    root_id = None
    for nid, r in raw_nodes.items():
        ntype = s(r["Node Type"])
        if ntype == "ROOT":
            root_id = nid
        elif ntype == "DOMAIN":
            domains[s(r["Domain"])] = {"code": s(r["Domain"]), "node_id": nid, "name": s(r["Node"]),
                                       "subject": s(r["공식과목"]), "memo": s(r["메모"])}
        elif ntype == "CLUSTER":
            clusters[s(r["Cluster"])] = {"code": s(r["Cluster"]), "node_id": nid, "name": s(r["Node"]),
                                         "domain": s(r["Domain"]), "stage": stage_num(r["Learning Stage"]),
                                         "memo": s(r["메모"])}
    cluster_by_node_id = {c["node_id"]: code for code, c in clusters.items()}
    domain_by_node_id = {d["node_id"]: code for code, d in domains.items()}
    cluster_by_name = {c["name"]: code for code, c in clusters.items()}
    domain_by_name = {d["name"]: code for code, d in domains.items()}

    name_to_id: dict[str, str] = {}
    for nid, r in raw_nodes.items():
        ntype = s(r["Node Type"])
        if ntype in STRUCT_TYPES:
            continue
        name = s(r["Node"])
        if name in name_to_id:
            raise SystemExit(f"duplicate concept name {name} ({name_to_id[name]}, {nid})")
        name_to_id[name] = nid
        nodes[nid] = {
            "id": nid, "name": name, "node_type": ntype,
            "source_cluster": s(r["Cluster"]), "cluster": s(r["Cluster"]), "domain": s(r["Domain"]),
            "official_subject": s(r["공식과목"]), "source_evidence_status": s(r["Evidence Status"]),
            "source_stage_label": s(r["Learning Stage"]),
            "current_rounds": i(r["현행회차수"]), "old_rounds": i(r["구범위회차수"]), "total_rounds": i(r["전체증거회차수"]),
            "mindmap_status": s(r["마인드맵 상태"]) or None, "original_parent_label": s(r["기존 상위 Concept"]) or None,
            "memo": s(r["메모"]) or None, "synthetic": False,
        }
    source_concept_ids = [nid for nid, n in nodes.items() if n["node_type"] in CONCEPT_TYPES]
    dialect_ids = [nid for nid, n in nodes.items() if n["node_type"] == "DIALECT"]

    # ---- curated (inferred) nodes ------------------------------------------
    inferred_items = {"nodes": [], "placements": [], "name_aliases": []}
    for sn in st.SYNTHETIC_NODES:
        if sn["name"] in name_to_id or sn["id"] in raw_nodes:
            raise SystemExit(f"curated node collides with source: {sn['name']}")
        cl = clusters[sn["cluster"]]
        nodes[sn["id"]] = {
            "id": sn["id"], "name": sn["name"], "node_type": sn["node_type"],
            "source_cluster": None, "cluster": sn["cluster"], "domain": cl["domain"],
            "official_subject": "과목 I" if cl["domain"] == "D1" else "과목 II",
            "source_evidence_status": "SYNTHETIC", "source_stage_label": None,
            "current_rounds": 0, "old_rounds": 0, "total_rounds": 0,
            "mindmap_status": None, "original_parent_label": None, "memo": None,
            "synthetic": True, "synthetic_kind": sn["kind"], "synthetic_basis": sn["basis"],
            "gap_family": sn.get("gap_family"), "inferred": True,
            "confidence": "medium" if sn["kind"] == "integration" else "high",
        }
        name_to_id[sn["name"]] = sn["id"]
        inferred_items["nodes"].append({"id": sn["id"], "name": sn["name"], "kind": sn["kind"],
                                        "cluster": sn["cluster"], "inferred": True, "reason": sn["basis"],
                                        "confidence": nodes[sn["id"]]["confidence"]})

    def nid_of(name: str) -> str:
        if name not in name_to_id:
            raise SystemExit(f"unknown concept name in curation: {name!r}")
        return name_to_id[name]

    # ---- placements: structure view = source, learning view = source + inferred placements
    for n in nodes.values():
        n["structure_cluster"] = n["source_cluster"] or n["cluster"]
    for name, (new_cluster, reason) in st.PLACEMENT_OVERRIDES.items():
        n = nodes[nid_of(name)]
        old = n["cluster"]
        n["cluster"] = new_cluster
        n["domain"] = clusters[new_cluster]["domain"]
        n["placement_override"] = {"from_cluster": old, "from_cluster_name": clusters[old]["name"],
                                   "from_stage": clusters[old]["stage"], "to_cluster": new_cluster,
                                   "to_cluster_name": clusters[new_cluster]["name"],
                                   "to_stage": clusters[new_cluster]["stage"], "reason": reason}
        inferred_items["placements"].append({"id": n["id"], "name": name, "view": "learning",
                                             **n["placement_override"], "inferred": True, "confidence": "high"})
    for n in nodes.values():
        cl = clusters[n["cluster"]]
        n["stage"] = cl["stage"]
        n["cluster_name"] = cl["name"]
        n["domain_name"] = domains[n["domain"]]["name"]
        scl = clusters[n["structure_cluster"]]
        n["structure_domain"] = scl["domain"]
        n["source_stage"] = scl["stage"]

    # ---- evidence sheets ---------------------------------------------------
    cur_ev = {s(r["Concept"]): r for r in sh["10_Current_Evidence"]}
    leg_ev = {s(r["Concept"]): r for r in sh["11_Legacy_Only"]}
    gap_ev = {s(r["Concept"]): r for r in sh["13_Current_Mindmap_Gaps"]}
    master = {s(r["Concept"]): r for r in sh["02_Concept_Master"]}
    for sheet, rows in (("10_Current_Evidence", cur_ev), ("11_Legacy_Only", leg_ev),
                        ("13_Current_Mindmap_Gaps", gap_ev)):
        for name in rows:
            if name not in name_to_id:
                broken_refs.append({"sheet": sheet, "ref": name, "kind": "concept name"})
    round_rows = defaultdict(list)
    for r in sh["03_Round_Concepts"]:
        round_rows[s(r["Concept"])].append({
            "year": i(r["연도"]), "round": i(r["회차"]), "role": s(r["역할"]), "era": s(r["범위시대"]),
            "strength": s(r["증거강도"]), "url": s(r["출처 URL"]), "memo": s(r["증거 메모"]),
        })
    for n in nodes.values():
        name = n["name"]
        m = master.get(name)
        all_rounds = parse_rounds(m["확인 회차"]) if m else []
        n["category"] = s(m["대분류"]) if m else None
        n["scope_status"] = s(m["범위 상태"]) if m else None
        n["current_round_list"] = sorted({x for x in all_rounds if x >= 52})
        n["old_round_list"] = sorted({x for x in all_rounds if x < 52})
        n["in_current_evidence"] = name in cur_ev
        n["in_legacy_only"] = name in leg_ev
        n["mindmap_gap"] = name in gap_ev
        n["mindmap_gap_action"] = s(gap_ev[name]["조치"]) if name in gap_ev else None
        if name in cur_ev:
            r = cur_ev[name]
            n["current_evidence"] = {"rounds": parse_rounds(r["현행 확인 회차"]), "first": i(r["최초 현행"]),
                                     "last": i(r["최근 현행"]), "strength": s(r["최고 증거강도"]),
                                     "source": s(r["대표 출처"]), "interpretation": s(r["해석"])}
        if name in leg_ev:
            r = leg_ev[name]
            n["legacy_evidence"] = {"rounds": parse_rounds(r["구범위 확인 회차"]), "first": i(r["최초 구범위"]),
                                    "last": i(r["최근 구범위"]), "strength": s(r["최고 증거강도"]),
                                    "source": s(r["대표 출처"]), "scope": s(r["범위 상태"]),
                                    "interpretation": s(r["해석"])}
    for nid in source_concept_ids:
        n = nodes[nid]
        es = n["source_evidence_status"]
        if es == "CURRENT_EVIDENCE" and not n["in_current_evidence"]:
            notes.append(f"{n['name']}: CURRENT_EVIDENCE but missing from 10_Current_Evidence")
        if es in ("OLDER_EVIDENCE_ONLY", "LEGACY") and not n["in_legacy_only"]:
            notes.append(f"{n['name']}: {es} but missing from 11_Legacy_Only")
    for n in nodes.values():
        n["is_legacy"], n["legacy_kind"] = False, None
        if n["synthetic"]:
            n["evidence_status"] = "integration" if n["synthetic_kind"] == "integration" else "structure"
        elif n["node_type"] == "DIALECT":
            n["evidence_status"] = "reference"
        elif n["in_current_evidence"]:
            n["evidence_status"] = "current"
        elif n["in_legacy_only"]:
            n["evidence_status"] = "legacy_only"
            n["is_legacy"] = True
            n["legacy_kind"] = "out_of_scope" if n["source_evidence_status"] == "LEGACY" else "older_evidence_only"
        else:
            n["evidence_status"] = "reference"

    # ---- 17 typed relations -------------------------------------------------
    edges_src = sh["17_KG_Edges"]
    for r in edges_src:
        for k in ("Source ID", "Target ID"):
            if s(r[k]) not in raw_nodes:
                broken_refs.append({"sheet": "17_KG_Edges", "ref": s(r[k]), "kind": "Node ID"})
    relation_counts = Counter(s(r["Relation Type"]) for r in edges_src)
    pair_relations = defaultdict(list)
    for r in edges_src:
        pair_relations[(s(r["Source ID"]), s(r["Target ID"]))].append(s(r["Relation Type"]))
    full = nx.MultiDiGraph()  # complete source graph, internal validation only
    for nid, r in raw_nodes.items():
        full.add_node(nid, name=s(r["Node"]), node_type=s(r["Node Type"]))
    for r in edges_src:
        full.add_edge(s(r["Source ID"]), s(r["Target ID"]), relation=s(r["Relation Type"]))

    def any_name(x):
        return nodes[x]["name"] if x in nodes else s(raw_nodes[x]["Node"])

    # =======================================================================
    # A. Concept Structure DAG
    # =======================================================================
    struct_nodes = {}
    struct_nodes[root_id] = {"id": root_id, "name": s(raw_nodes[root_id]["Node"]), "kind": "ROOT"}
    for code, d in domains.items():
        struct_nodes[d["node_id"]] = {"id": d["node_id"], "name": d["name"], "kind": "DOMAIN", "domain": code}
    for code, c in clusters.items():
        struct_nodes[c["node_id"]] = {"id": c["node_id"], "name": c["name"], "kind": "CLUSTER",
                                      "cluster": code, "domain": c["domain"]}
    for nid, n in nodes.items():
        struct_nodes[nid] = {"id": nid, "name": n["name"], "kind": "CONCEPT"}

    s_cand = {}
    for r in edges_src:
        rel = s(r["Relation Type"])
        if rel not in st.STRUCTURE_RELATIONS:
            continue
        a, b = s(r["Source ID"]), s(r["Target ID"])
        rec = s_cand.setdefault((a, b), {"source": a, "target": b, "relations": [], "reasons": [],
                                         "inferred": False, "provenance": []})
        rec["relations"].append(rel)
        rec["reasons"].append(s(r["Reason"]))
        rec["provenance"].append(f"17_KG_Edges:{rel}")
    # 17 links Domain→Cluster by *name*; for clusters whose name equals a concept name the edge points at
    # the concept's Node ID, leaving the cluster node detached. Attach those clusters from the source
    # 16_KG_Nodes Domain/Cluster columns (the same Domain > Cluster > Concept path as 19_Study_Outline_v2).
    has_parent = {b for (_, b) in s_cand}
    for code, c in clusters.items():
        if c["node_id"] in has_parent:
            continue
        d_id = domains[c["domain"]]["node_id"]
        s_cand[(d_id, c["node_id"])] = {"source": d_id, "target": c["node_id"], "relations": ["BELONGS_TO"],
                                        "reasons": ["16_KG_Nodes.Domain (19_Study_Outline_v2 Domain > Cluster)"],
                                        "inferred": False, "provenance": ["16_KG_Nodes.Domain", "19_Study_Outline_v2"]}
        same = name_to_id.get(c["name"])
        if same and nodes[same]["structure_cluster"] == code:
            s_cand[(c["node_id"], same)] = {"source": c["node_id"], "target": same, "relations": ["BELONGS_TO"],
                                            "reasons": ["16_KG_Nodes.Cluster (같은 이름 Concept의 소속 Cluster)"],
                                            "inferred": False, "provenance": ["16_KG_Nodes.Cluster", "19_Study_Outline_v2"]}
        notes.append(f"17_KG_Edges의 Domain→Cluster '{c['name']}' edge가 같은 이름 Concept({same})를 가리켜 "
                     f"Cluster 노드 {c['node_id']}를 16_KG_Nodes 기준으로 연결")
    struct_inferred = []

    def add_struct_inferred(a, b, reason, confidence="high"):
        if (a, b) in s_cand:
            return
        rec = {"source": a, "target": b, "relations": ["PART_OF"], "reasons": [reason], "inferred": True,
               "reason": reason, "confidence": confidence, "provenance": ["curation/structure.py"]}
        s_cand[(a, b)] = rec
        struct_inferred.append(rec)

    for nid, n in nodes.items():
        if not n["synthetic"]:
            continue
        p = st.SYNTHETIC_PARENTS.get(n["name"])
        if p:
            add_struct_inferred(nid_of(p), nid, f"'{n['name']}'은(는) '{p}' 아래의 학습용 그룹 노드. {n['synthetic_basis']}")
        else:
            add_struct_inferred(clusters[n["cluster"]]["node_id"], nid,
                                f"Stage 9 통합 노드를 {n['cluster']} Cluster 아래에 둠. {n['synthetic_basis']}", "medium")
    for child, parent in st.HIERARCHY_REPARENT.items():
        add_struct_inferred(nid_of(parent), nid_of(child),
                            josa(f"{child}은(는) '{parent}' 분류에 속함(원본 BELONGS_TO 부모는 유지)"))
    for rec in struct_inferred:
        rec["reason"] = josa(rec["reason"])
        rec["reasons"] = [rec["reason"]]

    s_excluded = []
    for (a, b), rec in list(s_cand.items()):
        if a in nodes and b in nodes:
            review = st.STRUCTURE_EDGE_REVIEW.get((nodes[a]["name"], nodes[b]["name"]))
            if review:
                s_excluded.append({**rec, **review, "source_name": nodes[a]["name"], "target_name": nodes[b]["name"]})
                del s_cand[(a, b)]
    s_candidate = nx.DiGraph()
    s_candidate.add_nodes_from(struct_nodes)
    s_candidate.add_edges_from(list(s_cand) + [(x["source"], x["target"]) for x in s_excluded])
    sg = nx.DiGraph()
    sg.add_nodes_from(struct_nodes)
    sg.add_edges_from(s_cand)
    structure_edges = []
    for (a, b), rec in s_cand.items():
        structure_edges.append({"source": a, "target": b, "source_name": any_name(a), "target_name": any_name(b),
                                "relation": rec["relations"][0], "relations": rec["relations"],
                                "inferred": rec["inferred"], "provenance": rec["provenance"],
                                "reason": rec.get("reason") or " / ".join(x for x in rec["reasons"] if x),
                                **({"confidence": rec["confidence"]} if rec["inferred"] else {})})

    # display parent (tree layout): curated grouping > concept parent in same cluster > any concept parent
    reparent_targets = {nid_of(c): nid_of(p) for c, p in st.HIERARCHY_REPARENT.items()}
    for nid, n in nodes.items():
        parents = [p for p in sg.predecessors(nid)]
        n["structure_parents"] = parents
        concept_parents = [p for p in parents if p in nodes]
        if nid in reparent_targets:
            disp = reparent_targets[nid]
        else:
            same = [p for p in concept_parents if nodes[p]["structure_cluster"] == n["structure_cluster"]]
            pick = same or concept_parents
            belongs = [p for p in pick if "BELONGS_TO" in s_cand[(p, nid)]["relations"]]
            disp = (belongs or pick or [None])[-1]
        n["hierarchy_parent"] = disp
        n["structure_children"] = sorted([c for c in sg.successors(nid) if c in nodes],
                                         key=lambda x: nodes[x]["name"])

    # =======================================================================
    # B. Learning DAG
    # =======================================================================
    content_rows = {s(r["Node ID"]): r for r in sh["21_Concept_Content"]}
    for nid, r in content_rows.items():
        if nid not in nodes:
            broken_refs.append({"sheet": "21_Concept_Content", "ref": nid, "kind": "Node ID"})
        elif s(r["Concept"]) != nodes[nid]["name"]:
            broken_refs.append({"sheet": "21_Concept_Content", "ref": f"{nid}={r['Concept']}", "kind": "ID/name mismatch"})

    explicit = {}

    def add_explicit(a, b, provenance, reason):
        rec = explicit.setdefault((a, b), {"source": a, "target": b, "origin": "explicit", "inferred": False,
                                           "provenance": [], "source_reasons": []})
        if provenance not in rec["provenance"]:
            rec["provenance"].append(provenance)
        if reason and reason not in rec["source_reasons"]:
            rec["source_reasons"].append(reason)

    metadata_relations = []
    for r in edges_src:
        rel = s(r["Relation Type"])
        a, b = s(r["Source ID"]), s(r["Target ID"])
        if rel in st.DAG_CANDIDATE_RELATIONS:
            add_explicit(a, b, f"17_KG_Edges:{rel}", s(r["Reason"]))
        elif rel not in ("BELONGS_TO",):
            metadata_relations.append({"source": a, "target": b, "relation": rel, "reason": s(r["Reason"]),
                                       "edge_class": s(r["Edge Class"]), "source_name": any_name(a),
                                       "target_name": any_name(b)})

    prereq_context = {}
    for nid, r in content_rows.items():
        ctx = {"concepts": [], "clusters": [], "domains": [], "unresolved": [], "raw": s(r["Prerequisites"])}
        for t in split_names(r["Prerequisites"]):
            if t in name_to_id and not nodes[name_to_id[t]]["synthetic"]:
                ctx["concepts"].append(name_to_id[t])
                if name_to_id[t] != nid:
                    is_parent = "BELONGS_TO" in pair_relations.get((name_to_id[t], nid), [])
                    add_explicit(name_to_id[t], nid, "21_Concept_Content.Prerequisites",
                                 "21_Concept_Content Prerequisites에 명시" + (" (상위 개념)" if is_parent else ""))
            elif t in cluster_by_name:
                ctx["clusters"].append(cluster_by_name[t])
            elif t in domain_by_name:
                ctx["domains"].append(domain_by_name[t])
            else:
                ctx["unresolved"].append(t)
                broken_refs.append({"sheet": "21_Concept_Content.Prerequisites", "ref": t, "kind": "name"})
        prereq_context[nid] = ctx

    excluded_explicit = []
    for (a, b), rec in list(explicit.items()):
        rec["relation"] = next((p.split(":")[1] for p in rec["provenance"] if p.startswith("17_KG_Edges:")), "REQUIRES")
        rec["source_relations"] = sorted(set(pair_relations.get((a, b), [])))
        rec["reason"] = " / ".join(rec["source_reasons"])
        review = st.EXPLICIT_EDGE_REVIEW.get((nodes[a]["name"], nodes[b]["name"]))
        if review:
            excluded_explicit.append({**rec, **review, "source_name": nodes[a]["name"], "target_name": nodes[b]["name"]})
            if review["decision"] == "reclassify_as_execution_order":
                metadata_relations.append({"source": a, "target": b, "relation": "EXECUTION_ORDER",
                                           "reason": review["reason"], "edge_class": "실행순서",
                                           "source_name": nodes[a]["name"], "target_name": nodes[b]["name"]})
            del explicit[(a, b)]

    explicit_graph = nx.DiGraph()
    explicit_graph.add_nodes_from(nodes)
    explicit_graph.add_edges_from(explicit)

    inferred, redundant_inferred, duplicate_inferred, conflicting_inferred = {}, [], [], []
    for src_name, dst_name, reason in prereq_mod.EDGES:
        a, b = nid_of(src_name), nid_of(dst_name)
        text = josa(reason.format(src=src_name, dst=dst_name))
        if (a, b) in explicit:
            explicit[(a, b)]["curated_reason"] = text
            duplicate_inferred.append([src_name, dst_name])
            continue
        if (a, b) in inferred:
            raise SystemExit(f"duplicate curated edge {src_name} -> {dst_name}")
        if nx.has_path(explicit_graph, a, b):
            redundant_inferred.append({"source_name": src_name, "target_name": dst_name,
                                       "why_skipped": "원본 explicit edge 경로로 이미 함의됨"})
            continue
        if nx.has_path(explicit_graph, b, a):
            path = nx.shortest_path(explicit_graph, b, a)
            conflicting_inferred.append({
                "source_name": src_name, "target_name": dst_name, "curated_reason": text,
                "decision": "rejected_conflicts_with_source",
                "reason": "원본 explicit 경로가 반대 방향(" + " → ".join(nodes[x]["name"] for x in path)
                          + ")이므로 source of truth를 따르고 이 inferred edge는 쓰지 않음"})
            continue
        rec = {"source": a, "target": b, "origin": "inferred", "inferred": True, "relation": "REQUIRES",
               "reason": text, "confidence": prereq_mod.confidence(src_name, dst_name),
               "provenance": ["curation/prerequisites.py"]}
        if pair_relations.get((a, b)) or pair_relations.get((b, a)):
            rec["related_source_relations"] = sorted(set(pair_relations.get((a, b), []))
                                                     | {x + "(reverse)" for x in pair_relations.get((b, a), [])})
        inferred[(a, b)] = rec

    learning_edges = list(explicit.values()) + list(inferred.values())
    for e in learning_edges:
        e["source_name"] = nodes[e["source"]]["name"]
        e["target_name"] = nodes[e["target"]]["name"]

    dag = nx.DiGraph()
    dag.add_nodes_from(nodes)
    dag.add_edges_from((e["source"], e["target"]) for e in learning_edges)
    l_candidate = dag.copy()
    l_candidate.add_edges_from((x["source"], x["target"]) for x in excluded_explicit)
    l_candidate.add_edges_from((nid_of(x["source_name"]), nid_of(x["target_name"])) for x in conflicting_inferred)
    conflict_pairs = {(nid_of(x["source_name"]), nid_of(x["target_name"])) for x in conflicting_inferred}

    # ---- cycle report (both graphs) ----------------------------------------
    def cyc_names(c, namer):
        return [namer(x) for x in c] + [namer(c[0])]

    def suspected(cycles, kind_of):
        cnt = Counter()
        for c in cycles:
            for a, b in zip(c, c[1:] + c[:1]):
                cnt[(a, b)] += 1
        return [{"source": any_name(a), "target": any_name(b), "cycles_involved": k, "kind": kind_of(a, b)}
                for (a, b), k in cnt.most_common()]

    excl_pairs = {(x["source"], x["target"]): x for x in excluded_explicit}

    def l_kind(a, b):
        if (a, b) in excl_pairs:
            return "explicit (" + ", ".join(excl_pairs[(a, b)]["provenance"]) + ") — 재검토 대상"
        if (a, b) in explicit:
            return "explicit (" + ", ".join(explicit[(a, b)]["provenance"]) + ")"
        if (a, b) in conflict_pairs:
            return "inferred — 원본과 충돌, 재검토 대상"
        return "inferred"

    s_excl_pairs = {(x["source"], x["target"]) for x in s_excluded}

    def s_kind(a, b):
        if (a, b) in s_excl_pairs:
            return "explicit 17_KG_Edges — 재검토 대상"
        return "inferred" if s_cand.get((a, b), {}).get("inferred") else "explicit 17_KG_Edges"

    l_cand_cycles = cycles_of(l_candidate)
    s_cand_cycles = cycles_of(s_candidate)
    naive = nx.DiGraph()
    for r in edges_src:
        rel = s(r["Relation Type"])
        if rel == "BELONGS_TO":
            continue
        a, b = s(r["Source ID"]), s(r["Target ID"])
        naive.add_edge(a, b, relation=rel)
        if rel in ("CONTRASTS", "DIALECT_EQUIVALENT"):
            naive.add_edge(b, a, relation=rel + "(symmetric)")
    naive_cycles = cycles_of(naive, 30)
    is_learning_dag = nx.is_directed_acyclic_graph(dag)
    is_structure_dag = nx.is_directed_acyclic_graph(sg)
    cycle_report = {
        "learning": {
            "graph": "learning",
            "is_dag": is_learning_dag,
            "cycles": [cyc_names(c, any_name) for c in cycles_of(dag)],
            "suspectedEdges": suspected(cycles_of(dag), l_kind),
            "pre_review_candidate_graph": {
                "description": "explicit 후보(21.Prerequisites Concept 토큰 ∪ 17 REQUIRES/PRECEDES/ENABLES/EXPLAINS) 전부 + "
                               "inferred edge. edge를 임의 삭제하지 않고 cycle을 기록한 뒤 prerequisite 관계만 재검토했다.",
                "is_dag": nx.is_directed_acyclic_graph(l_candidate),
                "cycles": [cyc_names(c, any_name) for c in l_cand_cycles],
                "suspectedEdges": suspected(l_cand_cycles, l_kind),
                "resolution": [{"edge": f"{x['source_name']} → {x['target_name']}", "provenance": x["provenance"],
                                "decision": x["decision"], "confidence": x["confidence"], "reason": x["reason"]}
                               for x in excluded_explicit]
                              + [{"edge": f"{x['source_name']} → {x['target_name']}", "provenance": ["curation/prerequisites.py"],
                                  "decision": x["decision"], "reason": x["reason"]} for x in conflicting_inferred],
            },
        },
        "structure": {
            "graph": "structure",
            "is_dag": is_structure_dag,
            "cycles": [cyc_names(c, any_name) for c in cycles_of(sg)],
            "suspectedEdges": suspected(cycles_of(sg), s_kind),
            "pre_review_candidate_graph": {
                "description": "17 BELONGS_TO + IS_A 전부 + inferred grouping edge.",
                "is_dag": nx.is_directed_acyclic_graph(s_candidate),
                "cycles": [cyc_names(c, any_name) for c in s_cand_cycles],
                "suspectedEdges": suspected(s_cand_cycles, s_kind),
                "resolution": [{"edge": f"{x['source_name']} → {x['target_name']}", "relations": x["relations"],
                                "decision": x["decision"], "confidence": x["confidence"], "reason": x["reason"]}
                               for x in s_excluded],
            },
        },
        "diagnostic_naive_all_typed_relations": {
            "description": "진단용: BELONGS_TO를 제외한 원본 typed relation 전부를 방향 간선으로 넣고 "
                           "CONTRASTS/DIALECT_EQUIVALENT를 대칭으로 취급한 그래프. 이런 관계를 DAG에 넣으면 cycle이 생긴다.",
            "is_dag": nx.is_directed_acyclic_graph(naive),
            "cycles": [cyc_names(c, any_name) for c in naive_cycles],
            "relations_in_cycles": sorted(Counter(
                naive.edges[a, b]["relation"] for c in naive_cycles for a, b in zip(c, c[1:] + c[:1])).items()),
        },
    }
    if not (is_learning_dag and is_structure_dag):
        DATA.mkdir(exist_ok=True)
        write_json(DATA / "cycle_report.json", cycle_report)
        raise SystemExit("DAG has cycles — see data/cycle_report.json (no edge was removed automatically)")

    # =======================================================================
    # C. Learning content (Excel 21–25 by Node ID) + supplementary notes
    # =======================================================================
    rules_rows = {}
    rules_by_node = defaultdict(list)
    for r in sh["22_Rules_And_Traps"]:
        rid, nid = s(r["Rule ID"]), s(r["Node ID"])
        if nid not in nodes:
            broken_refs.append({"sheet": "22_Rules_And_Traps", "ref": f"{rid}:{nid}", "kind": "Node ID"})
            continue
        if s(r["Concept"]) != nodes[nid]["name"]:
            broken_refs.append({"sheet": "22_Rules_And_Traps", "ref": f"{rid}:{nid}={r['Concept']}", "kind": "ID/name mismatch"})
        rules_rows[rid] = {"id": rid, "node": nid, "type": s(r["Rule Type"]), "rule": s(r["Rule"]), "why": s(r["Why"]),
                           "example": s(r["Example"]), "counterexample": s(r["Counterexample"]), "dbms": s(r["DBMS"]),
                           "evidence_status": s(r["Evidence Status"])}
        rules_by_node[nid].append(rid)

    def resolve_name(name, sheet, ref):
        if name in name_to_id:
            return name_to_id[name]
        if name in DIALECT_NAME_ALIASES:
            target, reason = DIALECT_NAME_ALIASES[name]
            inferred_items["name_aliases"].append({"sheet": sheet, "ref": ref, "name": name, "resolved_to": target,
                                                   "resolved_id": name_to_id[target], "inferred": True,
                                                   "reason": reason, "confidence": "high"})
            return name_to_id[target]
        broken_refs.append({"sheet": sheet, "ref": f"{ref}:{name}", "kind": "concept name"})
        return None

    comparisons, cmp_by_node = [], defaultdict(list)
    for r in sh["23_Comparisons"]:
        cid = s(r["Comparison ID"])
        a = resolve_name(s(r["Concept A"]), "23_Comparisons", cid)
        b = resolve_name(s(r["Concept B"]), "23_Comparisons", cid)
        comparisons.append({"id": cid, "a": a, "b": b, "a_name": s(r["Concept A"]), "b_name": s(r["Concept B"]),
                            "axis": s(r["Axis"]), "a_rule": s(r["A Rule"]), "b_rule": s(r["B Rule"]),
                            "example": s(r["Example"]), "exam_focus": s(r["Exam Focus"])})
        for x in (a, b):
            if x:
                cmp_by_node[x].append(cid)

    examples, ex_by_node = [], defaultdict(list)
    for r in sh["24_SQL_Examples"]:
        eid, nid = s(r["Example ID"]), s(r["Node ID"])
        if nid not in nodes:
            broken_refs.append({"sheet": "24_SQL_Examples", "ref": f"{eid}:{nid}", "kind": "Node ID"})
            continue
        examples.append({"id": eid, "node": nid, "type": s(r["Example Type"]), "sql": s(r["SQL / Pattern"]),
                         "purpose": s(r["Purpose"]), "expected_result": s(r["Expected Result"]), "dbms": s(r["DBMS"])})
        ex_by_node[nid].append(eid)

    dialects, dl_by_node = [], defaultdict(list)
    for r in sh["25_Dialect_Notes"]:
        did = s(r["Dialect ID"])
        nid = resolve_name(s(r["Concept"]), "25_Dialect_Notes", did)
        dialects.append({"id": did, "node": nid, "concept_name": s(r["Concept"]), "dbms": s(r["DBMS / Standard"]),
                         "behavior": s(r["Behavior"]), "exam_note": s(r["Exam Note"])})
        if nid:
            dl_by_node[nid].append(did)

    hubs = []
    for r in sh["20_Hubs_Rules"]:
        hub = s(r["Hub"])
        resolved, unresolved = [], []
        for t in split_names(r["Linked Concepts"]):
            names = content_mod.HUB_TOKEN_MAP.get(t) or ([t] if t in name_to_id else None)
            if names is None:
                unresolved.append(t)
            else:
                resolved.extend(nid_of(x) for x in names)
        hub_nodes = [nid_of(x) for x in content_mod.HUB_NODE_MAP.get(hub, [])]
        hubs.append({"hub": hub, "role": s(r["Role"]), "core_rule": s(r["Core Rule / Why it matters"]),
                     "edge_types": s(r["Edge Types"]), "study_note": s(r["Study Note"]),
                     "hub_nodes": hub_nodes, "linked": resolved, "unresolved_tokens": unresolved})
        for h in hub_nodes:
            for t in resolved:
                if t != h:
                    metadata_relations.append({"source": h, "target": t, "relation": "HUB_LINK",
                                               "reason": f"20_Hubs_Rules '{hub}' 허브의 Linked Concepts", "edge_class": "허브",
                                               "source_name": nodes[h]["name"], "target_name": nodes[t]["name"]})
    hub_by_node = defaultdict(list)
    for h in hubs:
        for x in h["hub_nodes"]:
            hub_by_node[x].append({"hub": h["hub"], "role": h["role"], "core_rule": h["core_rule"],
                                   "study_note": h["study_note"]})
    for src_name, targets in content_mod.RELATED.items():
        for t in targets:
            metadata_relations.append({"source": nid_of(src_name), "target": nid_of(t), "relation": "RELATED_TO",
                                       "reason": "curated(v0.4): 함께 확인하면 좋은 관련 개념 — 선수관계 아님",
                                       "edge_class": "관련", "source_name": src_name, "target_name": t,
                                       "inferred": True, "confidence": "medium"})

    content = {}
    for nid, n in nodes.items():
        r = content_rows.get(nid)
        if r is None:
            content[nid] = {"source": "none", "definition": "", "why_it_matters": "", "content_depth": None,
                            "review_flag": None, "rules": [], "traps": [], "comparisons": [], "examples": [],
                            "dialects": [], "hubs": hub_by_node.get(nid, []), "prerequisites_context": None}
            continue
        cmp_targets = [x for x in (resolve_name(t, "21_Concept_Content.Comparison Targets", nid)
                                   for t in split_names(r["Comparison Targets"])) if x]
        dl_targets = [x for x in (resolve_name(t, "21_Concept_Content.Dialect Notes", nid)
                                  for t in split_names(r["Dialect Notes"])) if x]
        rids = rules_by_node.get(nid, [])
        content[nid] = {
            "source": "21_Concept_Content",
            "definition": s(r["Definition"]), "why_it_matters": s(r["Why It Matters"]),
            "prerequisites_text": s(r["Prerequisites"]), "prerequisites_context": prereq_context[nid],
            "core_rule": s(r["Core Rule"]), "syntax": s(r["Syntax / Pattern"]), "exam_trap": s(r["Exam Trap"]),
            "comparison_targets": cmp_targets, "dialect_targets": dl_targets,
            "source_memo": s(r["Source / Memo"]), "content_depth": s(r["Content Depth"]) or None,
            "review_flag": s(r["Review Flag"]) or None,
            "rules": [x for x in rids if rules_rows[x]["type"] != "EXAM_TRAP"],
            "traps": [x for x in rids if rules_rows[x]["type"] == "EXAM_TRAP"],
            "comparisons": cmp_by_node.get(nid, []), "examples": ex_by_node.get(nid, []),
            "dialects": dl_by_node.get(nid, []), "hubs": hub_by_node.get(nid, []),
        }
        if n["name"] == "SQL 논리 실행 순서":
            content[nid]["execution_order"] = [{"edge": f"{x['source_name']} → {x['target_name']}", "note": x["reason"]}
                                               for x in excluded_explicit if x["decision"] == "reclassify_as_execution_order"]
    for nid in content_rows:
        if nid in nodes:
            nodes[nid]["content_depth"] = content[nid]["content_depth"]
            nodes[nid]["review_flag"] = content[nid]["review_flag"]

    # supplementary (v0.4 curated) — never replaces the workbook content
    supp_cmp = [{**{k: v for k, v in c.items() if k != "concepts"}, "concepts": [nid_of(x) for x in c["concepts"]],
                 "source": SUPPLEMENTARY_LABEL} for c in cmp_mod.COMPARISONS]
    supp_dl = [{**{k: v for k, v in d.items() if k != "concepts"}, "concepts": [nid_of(x) for x in d["concepts"]],
                "source": SUPPLEMENTARY_LABEL} for d in dialect_mod.DIALECTS]
    for name in list(content_mod.DEFINITIONS) + list(content_mod.RICH_RULES):
        nid_of(name)
    supplementary = {}
    for nid, n in nodes.items():
        rr = content_mod.RICH_RULES.get(n["name"], {})
        entry = {"definition": content_mod.DEFINITIONS.get(n["name"], ""), "why": rr.get("why", ""),
                 "core_rule": list(rr.get("rules", [])), "exam_traps": list(rr.get("traps", [])),
                 "dialect_notes": list(rr.get("dialect", [])), "examples": list(rr.get("examples", [])),
                 "comparisons": [c["id"] for c in supp_cmp if nid in c["concepts"]],
                 "dialects": [d["id"] for d in supp_dl if nid in d["concepts"]]}
        if any(entry.values()):
            supplementary[nid] = {**entry, "source": SUPPLEMENTARY_LABEL}
        if n["synthetic"]:  # curated nodes have no workbook row; their definition comes from curation
            content[nid].update({"source": "curated-node", "definition": entry["definition"],
                                 "why_it_matters": "", "content_depth": None})

    # =======================================================================
    # D. Stages, anchors, visibility, priority, tiers
    # =======================================================================
    stages = []
    for r in sh["18_Learning_DAG"]:
        num = i(r["Stage"])
        pre = s(r["선수 단계"])
        prereq = []
        for a, b in re.findall(r"(\d+)\s*[–-]\s*(\d+)", pre):
            prereq.extend(range(int(a), int(b) + 1))
        if not prereq:
            prereq = [int(x) for x in re.findall(r"\d+", pre)]
        stages.append({"stage": num, "order": num, "title": s(r["학습 블록"]), "goal": s(r["목표"]),
                       "prereq_text": pre, "prereq_stages": prereq,
                       "clusters": [c.strip() for c in s(r["포함 Cluster"]).split(",") if c.strip()],
                       "core_concepts_text": s(r["핵심 Concept"]), "meaning": s(r["구조적 의미"])})
    ls = dict(st.LEGACY_STAGE)
    ls["clusters"] = [c for c, v in clusters.items() if v["stage"] == "L"]
    ls.update(prereq_text="Stage 9", core_concepts_text="옵티마이저·실행계획·인덱스·물리 조인·분산 DB·PL/SQL·성능 모델링",
              meaning="기본 화면에서 숨김. Include Legacy 토글로만 표시.")
    stages.append(ls)
    for x in stages:
        missing = [c for c in x["clusters"] if c not in clusters]
        if missing:
            raise SystemExit(f"stage {x['stage']} references unknown clusters {missing}")

    lg = nx.DiGraph()
    for x in stages:
        lg.add_node(f"STAGE_{x['stage']}")
        for p in x["prereq_stages"]:
            lg.add_edge(f"STAGE_{p}", f"STAGE_{x['stage']}")
    for code, c in clusters.items():
        lg.add_edge(f"STAGE_{c['stage']}", f"CL_{code}")
    lg.add_nodes_from(nodes)
    lg.add_edges_from(dag.edges())
    roots = [nid for nid in nodes if dag.in_degree(nid) == 0]
    for nid in roots:
        lg.add_edge(f"CL_{nodes[nid]['cluster']}", nid)
    if not nx.is_directed_acyclic_graph(lg):
        raise SystemExit("anchored learning graph is not a DAG")

    base = {nid for nid, n in nodes.items() if not n["is_legacy"]}
    support = set()
    for nid in base:
        support |= {a for a in nx.ancestors(dag, nid) if nodes[a]["is_legacy"]}
        p = nodes[nid]["hierarchy_parent"]
        while p:
            if nodes[p]["is_legacy"]:
                support.add(p)
            p = nodes[p]["hierarchy_parent"]
    for nid, n in nodes.items():
        n["support"] = nid in support
        n["visible_by_default"] = nid in base or nid in support
        if nid in support:
            served = [d for d in nx.descendants(dag, nid) if d in base]
            n["support_for"] = sorted(nodes[x]["name"] for x in served)[:12]
            n["support_for_count"] = len(served)

    current = {nid for nid, n in nodes.items() if n["evidence_status"] == "current"}
    for nid, n in nodes.items():
        c = content[nid]
        n["exam_trap_count"] = len(c["traps"]) + (1 if c.get("exam_trap") and all(
            rules_rows[t]["rule"] != c["exam_trap"] for t in c["traps"]) else 0)
        n["has_comparison"] = bool(c["comparisons"] or c.get("comparison_targets"))
        n["current_successors"] = sum(1 for x in dag.successors(nid) if x in current)
    for nid, n in nodes.items():
        reasons = []
        cur = n["current_rounds"]
        if n["synthetic"] and n["synthetic_kind"] == "integration":
            n["priority"] = None
            continue
        if n["synthetic"] or n["evidence_status"] == "reference":
            n["priority"] = "C"
            reasons.append("현행 직접 증거가 없는 구조/참조 노드 — 다른 Concept 이해를 위한 보조")
        elif n["evidence_status"] == "current":
            signals = []
            if n["current_successors"]:
                signals.append(f"현행 Concept {n['current_successors']}개의 직접 선수")
            if n["exam_trap_count"]:
                signals.append(f"원본 시험 함정 {n['exam_trap_count']}개")
            if n["has_comparison"]:
                signals.append("원본 비교 카드/비교 대상")
            if cur >= 4 or (cur >= 2 and signals):
                n["priority"] = "A"
                reasons.append(f"현행 {cur}회 출제" + (" (반복)" if cur >= 2 else ""))
                reasons.extend(signals)
            else:
                n["priority"] = "B"
                reasons.append(f"현행 {cur}회 출제 확인")
        elif n["support"]:
            n["priority"] = "C"
            reasons.append(f"현행 증거 없음(구범위 {n['old_rounds']}회) — 현행 Concept "
                           f"{n.get('support_for_count', 0)}개의 선수/상위 개념이라 구조적으로 필요")
        else:
            n["priority"] = "Legacy"
            reasons.append("52회 이후 현행 출제 증거 없음" + (" · 현행 범위 밖(D7 등)" if n["legacy_kind"] == "out_of_scope" else ""))
        n["priority_reasons"] = reasons
    for nid, n in nodes.items():
        if n["priority"] is None:
            preds = list(dag.predecessors(nid))
            pa = [x for x in preds if nodes[x]["priority"] == "A"]
            n["priority"] = "A" if len(pa) >= 2 else "B"
            n["priority_reasons"] = [f"Stage 9 통합 복습 노드 — 선수 {len(preds)}개 중 Priority A {len(pa)}개"]

    hchildren = defaultdict(list)
    for nid, n in nodes.items():
        if n["hierarchy_parent"]:
            hchildren[n["hierarchy_parent"]].append(nid)
    for nid, n in nodes.items():
        vis_children = [c for c in hchildren[nid] if nodes[c]["visible_by_default"]]
        core = n["name"] in st.FORCE_CORE or n["priority"] == "A" or n["synthetic"] or len(vis_children) >= 2
        n["display_tier"] = "core" if n["visible_by_default"] and core else "detail"
        top = n["hierarchy_parent"] is None or nodes[n["hierarchy_parent"]]["structure_cluster"] != n["structure_cluster"]
        n["structure_top_level"] = top
        n["structure_tier"] = "core" if n["visible_by_default"] and (
            (top and n["priority"] in ("A", "B", "C")) or n["name"] in st.FORCE_CORE or len(vis_children) >= 2) else "detail"
        if not n["visible_by_default"]:
            n["legacy_display_tier"] = ("core" if n["name"] in st.FORCE_CORE or len(hchildren[nid]) >= 2
                                        or n["old_rounds"] >= 3 or top else "detail")
        n["hierarchy_children"] = sorted(hchildren[nid], key=lambda x: nodes[x]["name"])

    cluster_rank = {code: (stage_order(x["stage"]), k) for x in stages for k, code in enumerate(x["clusters"])}
    prio_rank = {"A": 0, "B": 1, "C": 2, "Legacy": 3}
    topo = list(nx.lexicographical_topological_sort(
        dag, key=lambda x: (cluster_rank[nodes[x]["cluster"]], prio_rank[nodes[x]["priority"]], nodes[x]["name"])))
    for k, nid in enumerate(topo):
        nodes[nid]["topo_index"] = k
    for nid in topo:
        n = nodes[nid]
        n["prerequisites"] = sorted(dag.predecessors(nid), key=lambda x: nodes[x]["topo_index"])
        n["next_concepts"] = sorted(dag.successors(nid), key=lambda x: nodes[x]["topo_index"])
        n["depth"] = 1 + max(nodes[p]["depth"] for p in n["prerequisites"]) if n["prerequisites"] else 0
        n["ancestor_count"] = len(nx.ancestors(dag, nid))
        n["aliases"] = content_mod.ALIASES.get(n["name"], [])
        n["learning_root"] = nid in roots

    # ---- clusters / domains output -----------------------------------------
    cluster_out = []
    for x in stages:
        for k, code in enumerate(x["clusters"]):
            c = clusters[code]
            members = [nid for nid, n in nodes.items() if n["cluster"] == code]
            smembers = [nid for nid, n in nodes.items() if n["structure_cluster"] == code]
            cluster_out.append({**c, "order": k, "stage_order": stage_order(c["stage"]),
                                "domain_name": domains[c["domain"]]["name"],
                                "concept_count": len(members), "structure_concept_count": len(smembers),
                                "current_count": sum(nodes[m]["evidence_status"] == "current" for m in members),
                                "legacy_hidden_count": sum(not nodes[m]["visible_by_default"] for m in members),
                                "root_concepts": [m for m in members if m in roots]})
    for x in stages:
        members = [nid for nid, n in nodes.items() if n["stage"] == x["stage"]]
        x["concept_count"] = len(members)
        x["current_count"] = sum(nodes[m]["evidence_status"] == "current" for m in members)
        x["default_visible_count"] = sum(nodes[m]["visible_by_default"] for m in members)
    domain_out = []
    for code, d in domains.items():
        members = [nid for nid, n in nodes.items() if n["structure_domain"] == code]
        domain_out.append({**d, "clusters": [c for c, v in clusters.items() if v["domain"] == code],
                           "concept_count": len(members),
                           "current_count": sum(nodes[m]["evidence_status"] == "current" for m in members)})

    gap_families = [{"family": s(r["개념/영역"]), "mindmap_status": s(r["마인드맵 상태"]), "scope": s(r["범위 상태"]),
                     "evidence": s(r["기출 근거"]), "action": s(r["추가 방식"])} for r in sh["04_Mindmap_Gaps"]]
    evidence = {nid: sorted(round_rows.get(n["name"], []), key=lambda r: r["round"]) for nid, n in nodes.items()}
    legacy_nodes = sorted(
        ({"id": nid, "name": n["name"], "cluster": n["cluster"], "stage": n["stage"], "legacy_kind": n["legacy_kind"],
          "old_rounds": n["old_rounds"], "old_round_list": n["old_round_list"],
          "shown_by_default_as_support": n["support"], "support_for": n.get("support_for", []),
          "priority": n["priority"]} for nid, n in nodes.items() if n["in_legacy_only"]),
        key=lambda x: (not x["shown_by_default_as_support"], x["cluster"], x["name"]))

    vault = scan_vault(nodes, name_to_id)

    inferred_edges = ([{**e, "graph": "learning"} for e in inferred.values()]
                      + [{**e, "graph": "structure"} for e in structure_edges if e["inferred"]])
    node_list = sorted(nodes.values(), key=lambda n: n["topo_index"])
    meta = {
        "source_file": xlsx.name,
        "total_source_concepts": len(source_concept_ids),
        "dialect_reference_nodes": len(dialect_ids),
        "synthetic_nodes": sum(n["synthetic"] for n in nodes.values()),
        "relation_counts": dict(relation_counts),
        "content_coverage_kpi": sh["26_Content_Coverage"],
        "curated_edges_duplicating_explicit": duplicate_inferred,
        "curated_edges_skipped_as_implied": redundant_inferred,
        "curated_edges_rejected_conflict": conflicting_inferred,
        "excluded_explicit_edges": [{k: x[k] for k in ("source_name", "target_name", "provenance", "decision", "confidence", "reason")}
                                    for x in excluded_explicit],
        "broken_references": broken_refs,
        "notes": notes,
    }
    return {
        "meta": meta, "stages": stages, "clusters": cluster_out, "domains": domain_out,
        "structure_nodes": [v for v in struct_nodes.values() if v["kind"] != "CONCEPT"],
        "nodes": node_list,
        "learning_edges": learning_edges, "structure_edges": structure_edges, "inferred_edges": inferred_edges,
        "inferred_items": inferred_items, "metadata_relations": metadata_relations,
        "content": content, "rules_and_traps": rules_rows, "comparisons": comparisons, "examples": examples,
        "dialects": dialects, "supplementary": {"label": SUPPLEMENTARY_LABEL, "notes": supplementary,
                                                "comparisons": supp_cmp, "dialects": supp_dl},
        "hubs": hubs, "gap_families": gap_families, "legacy_nodes": legacy_nodes, "evidence": evidence,
        "vault": vault, "cycle_report": cycle_report,
        "_graphs": {"dag": dag, "learning": lg, "structure": sg, "full": full, "roots": roots, "root_id": root_id},
    }


# ---------------------------------------------------------------------------
# Obsidian vault (read only): concept notes and mock-exam questions linking to concepts
# ---------------------------------------------------------------------------
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def scan_vault(nodes: dict, name_to_id: dict) -> dict:
    out = defaultdict(lambda: {"note": None, "questions": []})
    concepts_dir, questions_dir = REPO / "Concepts", REPO / "Questions"
    if concepts_dir.is_dir():
        for p in sorted(concepts_dir.glob("*.md")):
            nid = name_to_id.get(p.stem)
            if nid:
                out[nid]["note"] = f"Concepts/{p.name}"
    if questions_dir.is_dir():
        for p in sorted(questions_dir.glob("*.md")):
            text = p.read_text(encoding="utf-8")
            m = re.search(r"^#\s+(.+)$", text, re.M)
            title = m.group(1).strip() if m else p.stem
            for name in sorted({x.strip() for x in WIKILINK.findall(text)}):
                nid = name_to_id.get(name)
                if nid and not any(q["id"] == p.stem for q in out[nid]["questions"]):
                    out[nid]["questions"].append({"id": p.stem, "title": title, "path": f"Questions/{p.name}"})
    return {k: v for k, v in out.items() if v["note"] or v["questions"]}


# ---------------------------------------------------------------------------
# 3. Output
# ---------------------------------------------------------------------------
def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    args = ap.parse_args()

    out = build(args.xlsx)
    graphs = out.pop("_graphs")
    DATA.mkdir(exist_ok=True)
    WEB.mkdir(exist_ok=True)
    for old in ("hierarchy_edges.json", "rules.json"):  # superseded by concept_structure_edges / content
        (DATA / old).unlink(missing_ok=True)

    files = {
        "nodes.json": out["nodes"],
        "prerequisite_edges.json": out["learning_edges"],
        "concept_structure_edges.json": {"structure_nodes": out["structure_nodes"], "edges": out["structure_edges"]},
        "inferred_edges.json": {"edges": out["inferred_edges"], **out["inferred_items"]},
        "metadata_relations.json": out["metadata_relations"],
        "content.json": out["content"],
        "rules_and_traps.json": out["rules_and_traps"],
        "comparisons.json": out["comparisons"],
        "examples.json": out["examples"],
        "dialects.json": out["dialects"],
        "supplementary_notes.json": out["supplementary"],
        "stages.json": {"stages": out["stages"], "clusters": out["clusters"], "domains": out["domains"],
                        "hubs": out["hubs"], "gap_families": out["gap_families"]},
        "legacy_nodes.json": out["legacy_nodes"],
        "evidence.json": out["evidence"],
        "vault_links.json": out["vault"],
        "cycle_report.json": out["cycle_report"],
    }
    for fname, obj in files.items():
        write_json(DATA / fname, obj)

    report, ok = validate_graph.validate(DATA, meta=out["meta"])
    write_json(DATA / "validation_report.json", report)

    bundle = {k: out[k] for k in ("meta", "stages", "clusters", "domains", "structure_nodes", "nodes",
                                  "learning_edges", "structure_edges", "metadata_relations", "content",
                                  "rules_and_traps", "comparisons", "examples", "dialects", "supplementary",
                                  "hubs", "legacy_nodes", "evidence", "vault")}
    bundle["summary"] = report["summary"]
    (WEB / "data.js").write_text(
        "// Generated by scripts/build_learning_graph.py — do not edit by hand.\n"
        "window.SQLD_DATA = " + json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    validate_graph.print_summary(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
