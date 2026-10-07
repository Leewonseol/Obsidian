#!/usr/bin/env python3
"""Build the SQLD Learning DAG from SQLD_knowledge_graph_v0_4.xlsx.

Pipeline
  1. read the workbook (16/17/18/19/20/13/10/11/03/04 sheets)
  2. normalise nodes, hierarchy, evidence, legacy status
  3. build the prerequisite DAG = reviewed explicit edges (REQUIRES/PRECEDES/ENABLES/EXPLAINS)
                                + curated inferred edges (scripts/curation/prerequisites.py)
  4. cycle check on the candidate graph -> cycle_report.json (no edge is silently deleted)
  5. visibility / support / priority / display tier
  6. write data/*.json and web/data.js, then run validate_graph.validate()

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
sys.path.insert(0, str(ROOT / "scripts"))

from curation import comparisons as cmp_mod  # noqa: E402
from curation import content as content_mod  # noqa: E402
from curation import dialects as dialect_mod  # noqa: E402
from curation import prerequisites as prereq_mod  # noqa: E402
from curation import structure as st  # noqa: E402
import validate_graph  # noqa: E402

DATA = ROOT / "data"
WEB = ROOT / "web"
DEFAULT_XLSX = ROOT / "SQLD_knowledge_graph_v0_4.xlsx"

STRUCT_TYPES = {"ROOT", "DOMAIN", "CLUSTER"}
CONCEPT_TYPES = {"CONCEPT", "SYNTAX", "FUNCTION", "RULE"}


# ---------------------------------------------------------------------------
# 1. Workbook
# ---------------------------------------------------------------------------
def read_workbook(path: Path) -> dict[str, list[dict]]:
    import warnings

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    wanted = ["03_Round_Concepts", "04_Mindmap_Gaps", "10_Current_Evidence", "11_Legacy_Only",
              "13_Current_Mindmap_Gaps", "16_KG_Nodes", "17_KG_Edges", "18_Learning_DAG",
              "19_Study_Outline_v2", "20_Hubs_Rules", "02_Concept_Master"]
    sheets = {}
    for name in wanted:
        rows = list(wb[name].iter_rows(values_only=True))
        header = [str(h).strip() if h is not None else f"col{i}" for i, h in enumerate(rows[0])]
        out = []
        for r in rows[1:]:
            if r is None or all(v is None for v in r):
                continue
            out.append({header[i]: (r[i] if i < len(r) else None) for i in range(len(header))})
        sheets[name] = out
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


# ---------------------------------------------------------------------------
# 2. Normalise
# ---------------------------------------------------------------------------
def build(xlsx: Path) -> dict:
    sh = read_workbook(xlsx)
    report_notes: list[str] = []

    # ---- 16_KG_Nodes -------------------------------------------------------
    raw_nodes = {s(r["Node ID"]): r for r in sh["16_KG_Nodes"]}
    domains, clusters, nodes = {}, {}, {}
    for nid, r in raw_nodes.items():
        ntype = s(r["Node Type"])
        if ntype == "DOMAIN":
            domains[s(r["Domain"])] = {"code": s(r["Domain"]), "node_id": nid, "name": s(r["Node"]),
                                       "subject": s(r["공식과목"]), "memo": s(r["메모"])}
        elif ntype == "CLUSTER":
            clusters[s(r["Cluster"])] = {"code": s(r["Cluster"]), "node_id": nid, "name": s(r["Node"]),
                                         "domain": s(r["Domain"]), "stage": stage_num(r["Learning Stage"]),
                                         "memo": s(r["메모"])}

    name_to_id: dict[str, str] = {}
    for nid, r in raw_nodes.items():
        ntype = s(r["Node Type"])
        if ntype in STRUCT_TYPES:
            continue
        name = s(r["Node"])
        if name in name_to_id:
            raise ValueError(f"duplicate concept name {name}")
        name_to_id[name] = nid
        nodes[nid] = {
            "id": nid,
            "name": name,
            "node_type": ntype,
            "source_cluster": s(r["Cluster"]),
            "cluster": s(r["Cluster"]),
            "domain": s(r["Domain"]),
            "official_subject": s(r["공식과목"]),
            "source_evidence_status": s(r["Evidence Status"]),
            "source_stage_label": s(r["Learning Stage"]),
            "current_rounds": i(r["현행회차수"]),
            "old_rounds": i(r["구범위회차수"]),
            "total_rounds": i(r["전체증거회차수"]),
            "mindmap_status": s(r["마인드맵 상태"]) or None,
            "original_parent_label": s(r["기존 상위 Concept"]) or None,
            "memo": s(r["메모"]) or None,
            "synthetic": False,
        }

    source_concept_ids = [nid for nid, n in nodes.items() if n["node_type"] in CONCEPT_TYPES]
    dialect_ids = [nid for nid, n in nodes.items() if n["node_type"] == "DIALECT"]

    # ---- synthetic nodes ---------------------------------------------------
    for sn in st.SYNTHETIC_NODES:
        if sn["name"] in name_to_id:
            raise ValueError(f"synthetic node collides with source name: {sn['name']}")
        cl = clusters[sn["cluster"]]
        nodes[sn["id"]] = {
            "id": sn["id"], "name": sn["name"], "node_type": sn["node_type"],
            "source_cluster": None, "cluster": sn["cluster"], "domain": cl["domain"],
            "official_subject": "과목 II" if cl["domain"] != "D1" else "과목 I",
            "source_evidence_status": "SYNTHETIC", "source_stage_label": None,
            "current_rounds": 0, "old_rounds": 0, "total_rounds": 0,
            "mindmap_status": None, "original_parent_label": None, "memo": None,
            "synthetic": True, "synthetic_kind": sn["kind"], "synthetic_basis": sn["basis"],
            "gap_family": sn.get("gap_family"),
        }
        name_to_id[sn["name"]] = sn["id"]

    def nid_of(name: str) -> str:
        if name not in name_to_id:
            raise KeyError(f"unknown concept name in curation: {name!r}")
        return name_to_id[name]

    # ---- placement overrides ----------------------------------------------
    for name, (new_cluster, reason) in st.PLACEMENT_OVERRIDES.items():
        n = nodes[nid_of(name)]
        old = n["cluster"]
        n["cluster"] = new_cluster
        n["domain"] = clusters[new_cluster]["domain"]
        n["placement_override"] = {"from_cluster": old, "from_cluster_name": clusters[old]["name"],
                                   "from_stage": clusters[old]["stage"], "to_cluster": new_cluster,
                                   "to_cluster_name": clusters[new_cluster]["name"],
                                   "to_stage": clusters[new_cluster]["stage"], "reason": reason}
    for n in nodes.values():
        cl = clusters[n["cluster"]]
        n["stage"] = cl["stage"]
        n["cluster_name"] = cl["name"]
        n["domain_name"] = domains[n["domain"]]["name"]

    # ---- evidence sheets ---------------------------------------------------
    cur_ev = {s(r["Concept"]): r for r in sh["10_Current_Evidence"]}
    leg_ev = {s(r["Concept"]): r for r in sh["11_Legacy_Only"]}
    gap_ev = {s(r["Concept"]): r for r in sh["13_Current_Mindmap_Gaps"]}
    master = {s(r["Concept"]): r for r in sh["02_Concept_Master"]}
    round_rows = defaultdict(list)
    for r in sh["03_Round_Concepts"]:
        round_rows[s(r["Concept"])].append({
            "year": i(r["연도"]), "round": i(r["회차"]), "role": s(r["역할"]), "era": s(r["범위시대"]),
            "strength": s(r["증거강도"]), "url": s(r["출처 URL"]), "memo": s(r["증거 메모"]),
        })

    for nid, n in nodes.items():
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

    # cross-check: evidence status vs sheets
    for nid in source_concept_ids:
        n = nodes[nid]
        es = n["source_evidence_status"]
        if es == "CURRENT_EVIDENCE" and not n["in_current_evidence"]:
            report_notes.append(f"{n['name']}: CURRENT_EVIDENCE but missing from 10_Current_Evidence")
        if es in ("OLDER_EVIDENCE_ONLY", "LEGACY") and not n["in_legacy_only"]:
            report_notes.append(f"{n['name']}: {es} but missing from 11_Legacy_Only")

    # status classification
    for n in nodes.values():
        if n["synthetic"]:
            n["evidence_status"] = "integration" if n["synthetic_kind"] == "integration" else "structure"
            n["is_legacy"] = False
            n["legacy_kind"] = None
        elif n["node_type"] == "DIALECT":
            n["evidence_status"] = "reference"
            n["is_legacy"] = False
            n["legacy_kind"] = None
        elif n["in_current_evidence"]:
            n["evidence_status"] = "current"
            n["is_legacy"] = False
            n["legacy_kind"] = None
        elif n["in_legacy_only"]:
            n["evidence_status"] = "legacy_only"
            n["is_legacy"] = True
            n["legacy_kind"] = "out_of_scope" if n["source_evidence_status"] == "LEGACY" else "older_evidence_only"
        else:
            n["evidence_status"] = "reference"
            n["is_legacy"] = False
            n["legacy_kind"] = None

    # ---- hierarchy (BELONGS_TO by ID) -------------------------------------
    edges_src = sh["17_KG_Edges"]
    parents = defaultdict(list)
    for r in edges_src:
        if s(r["Relation Type"]) == "BELONGS_TO":
            parents[s(r["Target ID"])].append(s(r["Source ID"]))

    for nid, n in nodes.items():
        if n["synthetic"]:
            p = st.SYNTHETIC_PARENTS.get(n["name"])
            n["hierarchy_parent"] = nid_of(p) if p else None
            continue
        cands = parents.get(nid, [])
        concept_parents = [p for p in cands if p in nodes]
        n["hierarchy_parent"] = concept_parents[-1] if concept_parents else None
        if len(cands) > 1:
            n["source_parents"] = [raw_nodes[p]["Node"] for p in cands]
    for child, parent in st.HIERARCHY_REPARENT.items():
        nodes[nid_of(child)]["hierarchy_parent"] = nid_of(parent)
    for name, (parent, reason) in st.PRIMARY_PARENT_OVERRIDES.items():
        n = nodes[nid_of(name)]
        n["hierarchy_parent"] = nid_of(parent) if parent else None
        n["hierarchy_override_reason"] = reason
        report_notes.append(f"hierarchy override {name} → {parent or '(cluster)'}: {reason}")

    # guard against hierarchy cycles
    hg = nx.DiGraph()
    for nid, n in nodes.items():
        if n["hierarchy_parent"]:
            hg.add_edge(n["hierarchy_parent"], nid)
    if not nx.is_directed_acyclic_graph(hg):
        raise ValueError(f"hierarchy cycle: {nx.find_cycle(hg)}")

    # ---- full source graph (internal validation only) ---------------------
    full = nx.MultiDiGraph()
    for nid, r in raw_nodes.items():
        full.add_node(nid, name=s(r["Node"]), node_type=s(r["Node Type"]))
    for r in edges_src:
        full.add_edge(s(r["Source ID"]), s(r["Target ID"]), relation=s(r["Relation Type"]),
                      reason=s(r["Reason"]), edge_class=s(r["Edge Class"]))
    relation_counts = Counter(s(r["Relation Type"]) for r in edges_src)

    # ---- explicit prerequisite candidates ---------------------------------
    explicit = {}
    rejected_explicit = []
    metadata_relations = []
    for r in edges_src:
        rel = s(r["Relation Type"])
        src, dst = s(r["Source ID"]), s(r["Target ID"])
        if rel == "BELONGS_TO":
            continue
        rec = {"source": src, "target": dst, "relation": rel, "reason": s(r["Reason"]),
               "edge_class": s(r["Edge Class"]), "source_name": raw_nodes[src]["Node"],
               "target_name": raw_nodes[dst]["Node"]}
        if rel in st.DAG_CANDIDATE_RELATIONS:
            review = st.EXPLICIT_EDGE_REVIEW.get((rec["source_name"], rec["target_name"], rel))
            if review and review["decision"] != "accept":
                rejected_explicit.append({**rec, **review})
                metadata_relations.append({**rec, "relation": "EXECUTION_ORDER", "original_relation": rel,
                                           "review": review["reason"]})
                continue
            key = (src, dst)
            if key in explicit:
                explicit[key]["source_relations"].append(rel)
                explicit[key]["source_reasons"].append(rec["reason"])
            else:
                explicit[key] = {"source": src, "target": dst, "origin": "explicit", "inferred": False,
                                 "source_relations": [rel], "source_reasons": [rec["reason"]],
                                 "reason": rec["reason"]}
        else:
            metadata_relations.append(rec)

    # ---- inferred (curated) -----------------------------------------------
    pair_relations = defaultdict(list)
    for r in edges_src:
        rel = s(r["Relation Type"])
        if rel != "BELONGS_TO":
            a, b = s(r["Source ID"]), s(r["Target ID"])
            pair_relations[(a, b)].append(rel)
            pair_relations[(b, a)].append(rel + "(reverse)")

    inferred = {}
    curated_dup_explicit = []
    for src_name, dst_name, reason in prereq_mod.EDGES:
        a, b = nid_of(src_name), nid_of(dst_name)
        if a == b:
            raise ValueError(f"self loop in curation: {src_name}")
        text = josa(reason.format(src=src_name, dst=dst_name))
        if (a, b) in explicit:
            explicit[(a, b)]["curated_reason"] = text
            curated_dup_explicit.append([src_name, dst_name])
            continue
        if (a, b) in inferred:
            raise ValueError(f"duplicate curated edge {src_name} -> {dst_name}")
        rec = {"source": a, "target": b, "origin": "inferred", "inferred": True, "reason": text}
        if (a, b) in pair_relations:
            rec["related_source_relations"] = sorted(set(pair_relations[(a, b)]))
        inferred[(a, b)] = rec

    prereq_edges = list(explicit.values()) + list(inferred.values())
    for e in prereq_edges:
        e["source_name"] = nodes[e["source"]]["name"]
        e["target_name"] = nodes[e["target"]]["name"]

    # ---- candidate graph / cycle report -----------------------------------
    dag = nx.DiGraph()
    dag.add_nodes_from(nodes)
    for e in prereq_edges:
        dag.add_edge(e["source"], e["target"])

    candidate = dag.copy()
    for rj in rejected_explicit:
        candidate.add_edge(rj["source"], rj["target"])
    cand_cycles = list(nx.simple_cycles(candidate)) if not nx.is_directed_acyclic_graph(candidate) else []
    cand_cycles = sorted(cand_cycles, key=len)[:50]
    rejected_pairs = {(rj["source"], rj["target"]) for rj in rejected_explicit}

    def cyc_names(c):
        return [nodes[x]["name"] for x in c] + [nodes[c[0]]["name"]]

    suspected = Counter()
    for c in cand_cycles:
        for a, b in zip(c, c[1:] + c[:1]):
            suspected[(a, b)] += 1

    def edge_kind(a, b):
        if (a, b) in rejected_pairs:
            rel = next(x["relation"] for x in rejected_explicit if (x["source"], x["target"]) == (a, b))
            return f"explicit:{rel} (재검토 대상)"
        if (a, b) in explicit:
            return "explicit:" + ",".join(explicit[(a, b)]["source_relations"])
        return "inferred"

    # naive diagnostic: every typed source relation as a directed edge (+ symmetric CONTRASTS)
    naive = nx.DiGraph()
    for r in edges_src:
        rel = s(r["Relation Type"])
        if rel == "BELONGS_TO":
            continue
        a, b = s(r["Source ID"]), s(r["Target ID"])
        naive.add_edge(a, b, relation=rel)
        if rel in ("CONTRASTS", "DIALECT_EQUIVALENT"):
            naive.add_edge(b, a, relation=rel + "(symmetric)")
    naive_cycles = [] if nx.is_directed_acyclic_graph(naive) else sorted(nx.simple_cycles(naive), key=len)[:30]

    is_dag = nx.is_directed_acyclic_graph(dag)
    final_cycles = [] if is_dag else [cyc_names(c) for c in sorted(nx.simple_cycles(dag), key=len)[:50]]

    cycle_report = {
        "is_dag": is_dag,
        "cycles": final_cycles,
        "suspected_edges": [] if is_dag else None,
        "pre_review_candidate_graph": {
            "description": "명시 후보(REQUIRES/PRECEDES/ENABLES/EXPLAINS) 전부 + curated inferred edge로 만든 후보 그래프. "
                           "edge를 임의 삭제하지 않고 cycle을 기록한 뒤 prerequisite 관계만 재검토했다.",
            "is_dag": nx.is_directed_acyclic_graph(candidate),
            "cycles": [cyc_names(c) for c in cand_cycles],
            "suspected_edges": [
                {"source": nodes[a]["name"], "target": nodes[b]["name"], "cycles_involved": cnt,
                 "kind": edge_kind(a, b)}
                for (a, b), cnt in suspected.most_common()
            ],
            "resolution": [
                {"edge": f"{rj['source_name']} -[{rj['relation']}]-> {rj['target_name']}",
                 "decision": rj["decision"], "reason": rj["reason"]}
                for rj in rejected_explicit
            ],
        },
        "diagnostic_naive_all_typed_relations": {
            "description": "진단용: BELONGS_TO를 제외한 원본 typed relation을 전부 방향 간선으로 넣고 "
                           "CONTRASTS/DIALECT_EQUIVALENT를 대칭으로 취급한 그래프. 이런 관계가 DAG에 들어가면 cycle이 생김을 보여준다.",
            "is_dag": nx.is_directed_acyclic_graph(naive),
            "cycles": [[raw_nodes[x]["Node"] for x in c] + [raw_nodes[c[0]]["Node"]] for c in naive_cycles],
            "relations_in_cycles": sorted(Counter(
                naive.edges[a, b]["relation"] for c in naive_cycles for a, b in zip(c, c[1:] + c[:1])
            ).items()),
        },
    }
    if not is_dag:
        # Do not try to "fix" anything automatically; write the report and stop.
        DATA.mkdir(exist_ok=True)
        write_json(DATA / "cycle_report.json", cycle_report)
        raise SystemExit("Learning DAG has cycles — see data/cycle_report.json")

    # ---- metadata relations (non-DAG) -------------------------------------
    hubs = []
    for r in sh["20_Hubs_Rules"]:
        hub = s(r["Hub"])
        linked_tokens = [t.strip() for t in s(r["Linked Concepts"]).split(",") if t.strip()]
        resolved, unresolved = [], []
        for t in linked_tokens:
            names = content_mod.HUB_TOKEN_MAP.get(t)
            if names is None and t in name_to_id:
                names = [t]
            if names is None:
                unresolved.append(t)
                continue
            resolved.extend(nid_of(x) for x in names)
        hub_nodes = [nid_of(x) for x in content_mod.HUB_NODE_MAP.get(hub, [])]
        hubs.append({"hub": hub, "role": s(r["Role"]), "core_rule": s(r["Core Rule / Why it matters"]),
                     "edge_types": s(r["Edge Types"]), "study_note": s(r["Study Note"]),
                     "hub_nodes": hub_nodes, "linked": resolved, "unresolved_tokens": unresolved})
        for h in hub_nodes:
            for t in resolved:
                if t != h:
                    metadata_relations.append({"source": h, "target": t, "relation": "HUB_LINK",
                                               "reason": f"20_Hubs_Rules '{hub}' 허브의 Linked Concepts",
                                               "edge_class": "허브", "source_name": nodes[h]["name"],
                                               "target_name": nodes[t]["name"]})

    for src_name, targets in content_mod.RELATED.items():
        for t in targets:
            a, b = nid_of(src_name), nid_of(t)
            metadata_relations.append({"source": a, "target": b, "relation": "RELATED_TO",
                                       "reason": "curated: 함께 확인하면 좋은 관련 개념(선수관계 아님)",
                                       "edge_class": "관련", "source_name": src_name, "target_name": t})

    # ---- stages -----------------------------------------------------------
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
    ls["prereq_text"] = "Stage 9"
    ls["core_concepts_text"] = "옵티마이저·실행계획·인덱스·물리 조인·분산 DB·PL/SQL·성능 모델링"
    ls["meaning"] = "기본 화면에서 숨김. Include Legacy 토글로만 표시."
    stages.append(ls)
    stage_by_key = {x["stage"]: x for x in stages}
    for x in stages:
        missing = [c for c in x["clusters"] if c not in clusters]
        if missing:
            raise ValueError(f"stage {x['stage']} references unknown clusters {missing}")

    # ---- learning graph with anchors --------------------------------------
    lg = nx.DiGraph()
    for x in stages:
        lg.add_node(f"STAGE_{x['stage']}", kind="stage")
    for x in stages:
        for p in x["prereq_stages"]:
            lg.add_edge(f"STAGE_{p}", f"STAGE_{x['stage']}", kind="backbone")
    for code, c in clusters.items():
        lg.add_node(f"CL_{code}", kind="cluster")
        lg.add_edge(f"STAGE_{c['stage']}", f"CL_{code}", kind="anchor")
    for nid, n in nodes.items():
        lg.add_node(nid, kind="concept")
    for e in prereq_edges:
        lg.add_edge(e["source"], e["target"], kind="prerequisite")
    roots = [nid for nid in nodes if dag.in_degree(nid) == 0]
    for nid in roots:
        lg.add_edge(f"CL_{nodes[nid]['cluster']}", nid, kind="anchor")
    if not nx.is_directed_acyclic_graph(lg):
        raise SystemExit("anchored learning graph is not a DAG")
    backbone_reduced = nx.transitive_reduction(
        nx.DiGraph([(a, b) for a, b, d in lg.edges(data=True) if d["kind"] == "backbone"]))

    # ---- rules content ----------------------------------------------------
    comps = []
    for c in cmp_mod.COMPARISONS:
        comps.append({**{k: v for k, v in c.items() if k != "concepts"},
                      "concepts": [nid_of(x) for x in c["concepts"]]})
    dials = []
    for d in dialect_mod.DIALECTS:
        dials.append({**{k: v for k, v in d.items() if k != "concepts"},
                      "concepts": [nid_of(x) for x in d["concepts"]]})
    comp_by_node = defaultdict(list)
    for c in comps:
        for x in c["concepts"]:
            comp_by_node[x].append(c["id"])
    dial_by_node = defaultdict(list)
    for d in dials:
        for x in d["concepts"]:
            dial_by_node[x].append(d["id"])

    for name in list(content_mod.DEFINITIONS) + list(content_mod.RICH_RULES):
        nid_of(name)  # raises on typos

    hub_by_node = defaultdict(list)
    for h in hubs:
        for x in h["hub_nodes"]:
            hub_by_node[x].append(h)

    rules = {}
    for nid, n in nodes.items():
        rr = content_mod.RICH_RULES.get(n["name"], {})
        hub_cards = [{"hub": h["hub"], "role": h["role"], "core_rule": h["core_rule"], "study_note": h["study_note"]}
                     for h in hub_by_node.get(nid, [])]
        core_rule = list(rr.get("rules", []))
        for h in hub_cards:
            if h["core_rule"] not in core_rule:
                core_rule.insert(0, h["core_rule"])
        rules[nid] = {
            "definition": content_mod.DEFINITIONS.get(n["name"], ""),
            "why_it_matters": rr.get("why", ""),
            "core_rule": core_rule,
            "exam_traps": list(rr.get("traps", [])),
            "comparisons": comp_by_node.get(nid, []),
            "dialect_notes": list(rr.get("dialect", [])),
            "dialects": dial_by_node.get(nid, []),
            "examples": list(rr.get("examples", [])),
            "hubs": hub_cards,
        }
        if n["name"] == "SQL 논리 실행 순서":
            rules[nid]["execution_order"] = [
                {"edge": f"{rj['source_name']} → {rj['target_name']}", "note": rj["reason"]} for rj in rejected_explicit
            ] + [{"edge": "WHERE → GROUP BY → HAVING → SELECT → ORDER BY",
                  "note": "17_KG_Edges PRECEDES 체인(논리적 실행 순서)"}]

    # ---- visibility / support ---------------------------------------------
    base = {nid for nid, n in nodes.items() if not n["is_legacy"]}
    support = set()
    for nid in base:
        for a in nx.ancestors(dag, nid):
            if nodes[a]["is_legacy"]:
                support.add(a)
        p = nodes[nid]["hierarchy_parent"]
        while p:
            if nodes[p]["is_legacy"]:
                support.add(p)
            p = nodes[p]["hierarchy_parent"]
    support_sources = defaultdict(set)
    for s_id in support:
        for d in nx.descendants(dag, s_id):
            if d in base:
                support_sources[s_id].add(d)
    for nid, n in nodes.items():
        n["support"] = nid in support
        n["visible_by_default"] = (nid in base) or (nid in support)
        if nid in support:
            n["support_for"] = sorted(nodes[x]["name"] for x in support_sources[nid])[:12]
            n["support_for_count"] = len(support_sources[nid])

    # ---- priority ---------------------------------------------------------
    current = {nid for nid, n in nodes.items() if n["evidence_status"] == "current"}
    for nid, n in nodes.items():
        reasons = []
        succ_current = [x for x in dag.successors(nid) if x in current]
        traps = len(rules[nid]["exam_traps"])
        in_cmp = bool(rules[nid]["comparisons"])
        cur = n["current_rounds"]
        if n["synthetic"] and n["synthetic_kind"] == "integration":
            n["priority"] = None  # decided after every concept has a priority (see below)
            continue
        if n["synthetic"] or n["evidence_status"] == "reference":
            n["priority"] = "C"
            reasons.append("현행 직접 증거가 없는 구조/참조 노드 — 다른 Concept 이해를 위한 보조")
        elif n["evidence_status"] == "current":
            repeated = cur >= 2
            if cur >= 4 or (repeated and (succ_current or traps >= 2 or in_cmp)):
                n["priority"] = "A"
                reasons.append(f"현행 {cur}회 출제" + (" (반복)" if repeated else ""))
                if succ_current:
                    reasons.append(f"현행 Concept {len(succ_current)}개의 직접 선수")
                if traps >= 2:
                    reasons.append(f"시험 함정 {traps}개")
                if in_cmp:
                    reasons.append("시험 비교 카드 대상")
            else:
                n["priority"] = "B"
                reasons.append(f"현행 {cur}회 출제 확인")
        elif n["support"]:
            n["priority"] = "C"
            reasons.append(f"현행 증거 없음(구범위 {n['old_rounds']}회) — 현행 Concept {n.get('support_for_count', 0)}개의 선수/상위 개념이라 구조적으로 필요")
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

    # ---- display tier -----------------------------------------------------
    hchildren = defaultdict(list)
    for nid, n in nodes.items():
        if n["hierarchy_parent"]:
            hchildren[n["hierarchy_parent"]].append(nid)
    for nid, n in nodes.items():
        vis_children = [c for c in hchildren[nid] if nodes[c]["visible_by_default"]]
        if n["name"] in st.FORCE_DETAIL:
            tier = "detail"
        elif not n["visible_by_default"]:
            tier = "detail"
        elif (n["name"] in st.FORCE_CORE or n["priority"] == "A" or n["synthetic"]
              or len(vis_children) >= 2):
            tier = "core"
        else:
            tier = "detail"
        n["display_tier"] = tier
        if not n["visible_by_default"]:
            # tier used only when the viewer turns on "Include Legacy"
            n["legacy_display_tier"] = ("core" if n["name"] in st.FORCE_CORE or len(hchildren[nid]) >= 2
                                        or n["old_rounds"] >= 3 else "detail")
        n["hierarchy_children"] = sorted(hchildren[nid], key=lambda x: nodes[x]["name"])

    # ---- topological order (default learning path) ------------------------
    cluster_rank = {}
    for x in stages:
        for k, code in enumerate(x["clusters"]):
            cluster_rank[code] = (stage_order(x["stage"]), k)
    prio_rank = {"A": 0, "B": 1, "C": 2, "Legacy": 3}
    topo = list(nx.lexicographical_topological_sort(
        dag, key=lambda x: (cluster_rank[nodes[x]["cluster"]], prio_rank[nodes[x]["priority"]], nodes[x]["name"])))
    for k, nid in enumerate(topo):
        nodes[nid]["topo_index"] = k
    for nid, n in nodes.items():
        n["prerequisites"] = sorted(dag.predecessors(nid), key=lambda x: nodes[x]["topo_index"])
        n["next_concepts"] = sorted(dag.successors(nid), key=lambda x: nodes[x]["topo_index"])
        n["depth"] = 0
    for nid in topo:
        preds = list(dag.predecessors(nid))
        nodes[nid]["depth"] = 1 + max(nodes[p]["depth"] for p in preds) if preds else 0
    for nid, n in nodes.items():
        n["ancestor_count"] = len(nx.ancestors(dag, nid))
        n["aliases"] = content_mod.ALIASES.get(n["name"], [])

    # ---- hierarchy edges --------------------------------------------------
    hierarchy_edges = []
    for x in stages:
        for code in x["clusters"]:
            hierarchy_edges.append({"source": f"STAGE_{x['stage']}", "target": code, "type": "STAGE_CLUSTER"})
    for nid, n in nodes.items():
        hierarchy_edges.append({"source": n["cluster"], "target": nid, "type": "CLUSTER_CONCEPT",
                                "is_root_anchor": nid in roots,
                                "is_top_level": n["hierarchy_parent"] is None or nodes[n["hierarchy_parent"]]["cluster"] != n["cluster"]})
        if n["hierarchy_parent"]:
            hierarchy_edges.append({"source": n["hierarchy_parent"], "target": nid, "type": "PARENT_CHILD",
                                    "cross_cluster": nodes[n["hierarchy_parent"]]["cluster"] != n["cluster"]})

    # ---- clusters output --------------------------------------------------
    cluster_out = []
    for x in stages:
        for k, code in enumerate(x["clusters"]):
            c = clusters[code]
            members = [nid for nid, n in nodes.items() if n["cluster"] == code]
            cluster_out.append({**c, "order": k, "stage_order": stage_order(c["stage"]),
                                "domain_name": domains[c["domain"]]["name"],
                                "concept_count": len(members),
                                "current_count": sum(nodes[m]["evidence_status"] == "current" for m in members),
                                "legacy_hidden_count": sum(not nodes[m]["visible_by_default"] for m in members)})
    for x in stages:
        members = [nid for nid, n in nodes.items() if n["stage"] == x["stage"]]
        x["concept_count"] = len(members)
        x["current_count"] = sum(nodes[m]["evidence_status"] == "current" for m in members)
        x["default_visible_count"] = sum(nodes[m]["visible_by_default"] for m in members)
        x["backbone_prereq_reduced"] = sorted(
            int(a.split("_")[1]) if a.split("_")[1] != "L" else "L"
            for a, b in backbone_reduced.edges() if b == f"STAGE_{x['stage']}")

    # ---- gap families -----------------------------------------------------
    gap_families = []
    for r in sh["04_Mindmap_Gaps"]:
        fam = s(r["개념/영역"])
        gap_families.append({"family": fam, "mindmap_status": s(r["마인드맵 상태"]),
                             "scope": s(r["범위 상태"]), "evidence": s(r["기출 근거"]),
                             "action": s(r["추가 방식"]),
                             "matched_nodes": [nid for nid, n in nodes.items()
                                               if n["name"] == fam or n.get("gap_family") == fam]})

    # ---- evidence output --------------------------------------------------
    evidence = {nid: sorted(round_rows.get(n["name"], []), key=lambda r: r["round"]) for nid, n in nodes.items()}

    # ---- legacy nodes -----------------------------------------------------
    legacy_nodes = []
    for nid, n in nodes.items():
        if n["in_legacy_only"]:
            legacy_nodes.append({"id": nid, "name": n["name"], "cluster": n["cluster"], "stage": n["stage"],
                                 "legacy_kind": n["legacy_kind"], "old_rounds": n["old_rounds"],
                                 "old_round_list": n["old_round_list"],
                                 "shown_by_default_as_support": n["support"],
                                 "support_for": n.get("support_for", []),
                                 "priority": n["priority"]})
    legacy_nodes.sort(key=lambda x: (not x["shown_by_default_as_support"], x["cluster"], x["name"]))

    # ---- assemble ---------------------------------------------------------
    node_list = sorted(nodes.values(), key=lambda n: n["topo_index"])
    meta = {
        "source_file": xlsx.name,
        "total_source_concepts": len(source_concept_ids),
        "dialect_reference_nodes": len(dialect_ids),
        "synthetic_nodes": sum(n["synthetic"] for n in nodes.values()),
        "relation_counts": dict(relation_counts),
        "curated_edges_duplicating_explicit": curated_dup_explicit,
        "notes": report_notes,
    }
    out = {
        "meta": meta,
        "stages": stages,
        "clusters": cluster_out,
        "domains": list(domains.values()),
        "nodes": node_list,
        "prerequisite_edges": prereq_edges,
        "inferred_edges": list(inferred.values()),
        "hierarchy_edges": hierarchy_edges,
        "metadata_relations": metadata_relations,
        "rules": rules,
        "comparisons": comps,
        "dialects": dials,
        "hubs": hubs,
        "gap_families": gap_families,
        "legacy_nodes": legacy_nodes,
        "evidence": evidence,
        "cycle_report": cycle_report,
        "_graphs": {"dag": dag, "learning": lg, "full": full, "roots": roots},
    }
    return out


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

    files = {
        "nodes.json": out["nodes"],
        "prerequisite_edges.json": out["prerequisite_edges"],
        "inferred_edges.json": out["inferred_edges"],
        "hierarchy_edges.json": out["hierarchy_edges"],
        "metadata_relations.json": out["metadata_relations"],
        "rules.json": out["rules"],
        "comparisons.json": out["comparisons"],
        "dialects.json": out["dialects"],
        "stages.json": {"stages": out["stages"], "clusters": out["clusters"], "domains": out["domains"],
                        "hubs": out["hubs"], "gap_families": out["gap_families"]},
        "legacy_nodes.json": out["legacy_nodes"],
        "evidence.json": out["evidence"],
        "cycle_report.json": out["cycle_report"],
    }
    for fname, obj in files.items():
        write_json(DATA / fname, obj)

    report, ok = validate_graph.validate(DATA, graphs=graphs, meta=out["meta"])
    write_json(DATA / "validation_report.json", report)

    bundle = {k: out[k] for k in ("meta", "stages", "clusters", "domains", "nodes", "prerequisite_edges",
                                  "hierarchy_edges", "metadata_relations", "rules", "comparisons",
                                  "dialects", "hubs", "legacy_nodes", "evidence")}
    bundle["summary"] = report["summary"]
    (WEB / "data.js").write_text(
        "// Generated by scripts/build_learning_graph.py — do not edit by hand.\n"
        "window.SQLD_DATA = " + json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    validate_graph.print_summary(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
