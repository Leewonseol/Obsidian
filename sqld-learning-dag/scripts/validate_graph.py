#!/usr/bin/env python3
"""Validate the generated SQLD data (data/*.json): Concept Structure DAG, Learning DAG, coverage and
learning-content linkage.

Run standalone after a build:   python3 scripts/validate_graph.py [--write]
The build script also calls validate() and writes data/validation_report.json.

Everything is re-derived from the JSON files the web app loads, so this is an independent check.
Exit code is non-zero when a hard (error) check fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LEARNING_PROVENANCE = {"21_Concept_Content.Prerequisites", "17_KG_Edges:REQUIRES", "17_KG_Edges:PRECEDES",
                       "17_KG_Edges:ENABLES", "17_KG_Edges:EXPLAINS", "curation/prerequisites.py"}
STRUCTURE_RELATIONS = {"BELONGS_TO", "IS_A", "PART_OF"}
FORBIDDEN = {"CONTRASTS", "AFFECTS", "DIALECT", "DIALECT_OF", "DIALECT_EQUIVALENT", "EXCEPTION",
             "RELATED_TO", "CO_OCCURS_WITH"}
CONFIDENCE = {"high", "medium", "low"}
EXPECTED = {"source_concepts": 475, "current": 286, "legacy_only": 185, "gap": 191}


def load(data_dir: Path, name: str):
    return json.loads((data_dir / name).read_text(encoding="utf-8"))


def stage_order(stage) -> int:
    return 10 if stage == "L" else int(stage)


def validate(data_dir: Path = DATA, meta: dict | None = None):
    nodes = load(data_dir, "nodes.json")
    ledges = load(data_dir, "prerequisite_edges.json")
    sdata = load(data_dir, "concept_structure_edges.json")
    inf = load(data_dir, "inferred_edges.json")
    content = load(data_dir, "content.json")
    rules = load(data_dir, "rules_and_traps.json")
    comps = load(data_dir, "comparisons.json")
    examples = load(data_dir, "examples.json")
    dialects = load(data_dir, "dialects.json")
    stg = load(data_dir, "stages.json")
    legacy = load(data_dir, "legacy_nodes.json")
    cycle = load(data_dir, "cycle_report.json")

    checks = []

    def check(name, ok, detail="", hard=True):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:2000],
                       "severity": "error" if hard else "warning"})

    by_id = {n["id"]: n for n in nodes}
    source = [n for n in nodes if not n["synthetic"] and n["node_type"] != "DIALECT"]
    current = [n for n in source if n["evidence_status"] == "current"]
    legacy_only = [n for n in source if n["in_legacy_only"]]
    gap = [n for n in source if n["mindmap_gap"]]

    # ---- identity ---------------------------------------------------------
    check("Node ID 유일", len(by_id) == len(nodes))
    names = Counter(n["name"] for n in nodes)
    check("Concept 이름 → Node ID 매핑 중복 없음", all(v == 1 for v in names.values()),
          [k for k, v in names.items() if v > 1])
    check("Total source concepts = 475", len(source) == EXPECTED["source_concepts"], len(source))
    check("Current concepts = 286 (10_Current_Evidence)", len(current) == EXPECTED["current"], len(current))
    check("Legacy-only concepts = 185 보존 (11_Legacy_Only)", len(legacy_only) == EXPECTED["legacy_only"] == len(legacy),
          f"{len(legacy_only)} / legacy_nodes.json {len(legacy)}")
    check("Mindmap-gap concepts = 191 (13_Current_Mindmap_Gaps)", len(gap) == EXPECTED["gap"], len(gap))

    # ---- Learning DAG -----------------------------------------------------
    dag = nx.DiGraph()
    dag.add_nodes_from(by_id)
    bad_ref = [e for e in ledges if e["source"] not in by_id or e["target"] not in by_id]
    check("Learning edge의 Node ID 참조 유효", not bad_ref, len(bad_ref))
    dag.add_edges_from((e["source"], e["target"]) for e in ledges if not bad_ref)
    explicit = [e for e in ledges if not e["inferred"]]
    inferred = [e for e in ledges if e["inferred"]]
    bad_prov = [e for e in ledges if set(e["provenance"]) - LEARNING_PROVENANCE]
    check("Learning edge 출처는 21.Prerequisites / 17 REQUIRES·PRECEDES·ENABLES·EXPLAINS / curated inferred만",
          not bad_prov, [(e["source_name"], e["target_name"], e["provenance"]) for e in bad_prov][:10])
    forb = [e for e in ledges if e.get("relation") in FORBIDDEN]
    check("금지 관계(CONTRASTS·AFFECTS·DIALECT*·EXCEPTION·RELATED_TO·CO_OCCURS_WITH)가 Learning edge로 쓰이지 않음", not forb)
    bad_inf = [e for e in inferred if not e.get("reason") or e.get("confidence") not in CONFIDENCE]
    check("모든 inferred learning edge에 inferred=true·reason·confidence", not bad_inf, len(bad_inf))
    dup = [k for k, v in Counter((e["source"], e["target"]) for e in ledges).items() if v > 1]
    check("Learning edge 중복·self-loop 없음", not dup and not any(e["source"] == e["target"] for e in ledges))
    is_ldag = nx.is_directed_acyclic_graph(dag)
    check("networkx.is_directed_acyclic_graph(learning_graph)", is_ldag)
    check("cycle_report.learning.is_dag 일치", cycle["learning"]["is_dag"] == is_ldag)
    stage_viol = [f"{e['source_name']}(S{by_id[e['source']]['stage']}) → {e['target_name']}(S{by_id[e['target']]['stage']})"
                  for e in ledges if stage_order(by_id[e["source"]]["stage"]) > stage_order(by_id[e["target"]]["stage"])]
    check("학습 화면 Stage 단조성: 선수 Stage ≤ 다음 Stage", not stage_viol, "; ".join(stage_viol[:20]))

    stages = stg["stages"]
    clusters = {c["code"]: c for c in stg["clusters"]}
    lg = nx.DiGraph()
    for x in stages:
        lg.add_node(f"STAGE_{x['stage']}")
        for p in x["prereq_stages"]:
            lg.add_edge(f"STAGE_{p}", f"STAGE_{x['stage']}")
    for code, c in clusters.items():
        lg.add_edge(f"STAGE_{c['stage']}", f"CL_{code}")
    lg.add_edges_from(dag.edges())
    roots = [nid for nid in by_id if dag.in_degree(nid) == 0]
    for nid in roots:
        lg.add_edge(f"CL_{by_id[nid]['cluster']}", nid)
    check("Stage/Cluster anchor를 포함한 learning graph도 DAG", nx.is_directed_acyclic_graph(lg))
    reach = set()
    for x in stages:
        reach |= nx.descendants(lg, f"STAGE_{x['stage']}")
    l_orphans = [n["name"] for n in nodes if n["id"] not in reach]
    check("Learning graph orphan 없음(모든 노드가 Stage root에서 도달 가능)", not l_orphans, l_orphans[:20])
    cur_missing_learning = [n["name"] for n in current if n["id"] not in reach or not n["visible_by_default"]]
    gap_missing = [n["name"] for n in gap if n["id"] not in reach or not n["visible_by_default"]]
    check("Current concepts missing from learning system = 0", not cur_missing_learning, cur_missing_learning)
    check("Mindmap-gap concepts missing = 0", not gap_missing, gap_missing)

    # ---- Concept Structure DAG --------------------------------------------
    snodes = {x["id"]: x for x in sdata["structure_nodes"]}
    snodes.update({n["id"]: {"id": n["id"], "kind": "CONCEPT"} for n in nodes})
    sedges = sdata["edges"]
    sg = nx.DiGraph()
    sg.add_nodes_from(snodes)
    s_bad = [e for e in sedges if e["source"] not in snodes or e["target"] not in snodes]
    check("Structure edge의 Node ID 참조 유효", not s_bad, len(s_bad))
    sg.add_edges_from((e["source"], e["target"]) for e in sedges if not s_bad)
    s_rel_bad = [e for e in sedges if set(e["relations"]) - STRUCTURE_RELATIONS]
    check("Structure edge는 BELONGS_TO / IS_A / PART_OF만", not s_rel_bad,
          [(e["source_name"], e["target_name"], e["relations"]) for e in s_rel_bad][:10])
    s_inf_bad = [e for e in sedges if e["inferred"] and (not e.get("reason") or e.get("confidence") not in CONFIDENCE)]
    check("inferred structure edge에 reason·confidence", not s_inf_bad, len(s_inf_bad))
    is_sdag = nx.is_directed_acyclic_graph(sg)
    check("networkx.is_directed_acyclic_graph(concept_structure_graph)", is_sdag)
    check("cycle_report.structure.is_dag 일치", cycle["structure"]["is_dag"] == is_sdag)
    root = next(x for x in snodes.values() if x["kind"] == "ROOT")["id"]
    s_reach = nx.descendants(sg, root) if is_sdag else set()
    s_missing = [n["name"] for n in nodes if n["id"] not in s_reach]
    s_orphans = [snodes[x].get("name", x) for x in snodes if x != root and sg.in_degree(x) == 0]
    cur_missing_structure = [n["name"] for n in current if n["id"] not in s_reach]
    check("Concepts missing from structure DAG = 0", not s_missing, s_missing[:20])
    check("Current concepts missing from structure DAG = 0", not cur_missing_structure, cur_missing_structure)
    check("Structure DAG orphan(부모 없는 비-ROOT 노드) 없음", not s_orphans, s_orphans[:20])

    # ---- visibility -------------------------------------------------------
    broken_vis = [f"{by_id[p]['name']} → {n['name']}" for n in nodes if n["visible_by_default"]
                  for p in dag.predecessors(n["id"]) if not by_id[p]["visible_by_default"]]
    check("기본 화면 노드의 선수 노드도 기본 화면에 있음", not broken_vis, broken_vis[:20])
    oos = [n["name"] for n in nodes if n.get("legacy_kind") == "out_of_scope" and n["visible_by_default"]]
    check("현행 범위 밖 Legacy(D7 등)는 기본 화면에서 숨김", not oos, oos)

    # ---- inferred items ---------------------------------------------------
    items = [*inf["nodes"], *inf["placements"], *inf["name_aliases"]]
    check("inferred 노드·배치·이름 alias에 inferred=true·reason·confidence",
          all(x.get("inferred") and x.get("reason") and x.get("confidence") in CONFIDENCE for x in items))

    # ---- learning content -------------------------------------------------
    src_ids = {n["id"] for n in source}
    with_row = [nid for nid in src_ids if content[nid]["source"] == "21_Concept_Content"]
    no_def = [by_id[nid]["name"] for nid in src_ids if not content[nid]["definition"]]
    depth = Counter(content[nid]["content_depth"] for nid in src_ids)
    review_cur = sum(1 for n in current if content[n["id"]]["review_flag"] == "우선검토")
    kpi = (meta or {}).get("content_coverage_kpi") or {}
    check("475개 Concept 모두 21_Concept_Content 행과 연결", len(with_row) == len(src_ids), len(with_row))
    check("Definition 475개 로드", not no_def, no_def[:10])
    check("Content Depth(CURATED/TEMPLATE) 보존", set(depth) <= {"CURATED", "TEMPLATE"} and sum(depth.values()) == 475,
          dict(depth))
    if kpi:
        check("CURATED/TEMPLATE 수가 26_Content_Coverage KPI와 일치",
              depth.get("CURATED") == kpi.get("직접 작성/보강(CURATED)") and depth.get("TEMPLATE") == kpi.get("템플릿 기반 설명"),
              f"{dict(depth)} vs {kpi}")
        check("현행 우선검토 수가 26 KPI와 일치", review_cur == kpi.get("현행 중 우선검토 필요"), review_cur)
    rule_refs = Counter(r for c in content.values() for r in c.get("rules", []) + c.get("traps", []))
    check("22_Rules_And_Traps 모든 행이 Concept 상세에 정확히 1번 연결",
          set(rule_refs) == set(rules) and all(v == 1 for v in rule_refs.values()),
          f"{len(rule_refs)} / {len(rules)}")
    check("22 Rule의 Node ID 참조 유효", all(r["node"] in by_id for r in rules.values()))
    cmp_ok = all(c["a"] in by_id and c["b"] in by_id and c["id"] in content[c["a"]]["comparisons"]
                 and c["id"] in content[c["b"]]["comparisons"] for c in comps)
    check("23_Comparisons 양쪽 Concept 해석 및 상세 연결", cmp_ok)
    ex_ok = all(e["node"] in by_id and e["id"] in content[e["node"]]["examples"] for e in examples)
    check("24_SQL_Examples Node ID 유효 및 상세 연결", ex_ok)
    check("RESULT 예제는 Expected Result 보유", all(e["expected_result"] for e in examples if e["type"] == "RESULT"))
    dl_ok = all(d["node"] in by_id and d["id"] in content[d["node"]]["dialects"] for d in dialects)
    check("25_Dialect_Notes Concept 해석 및 상세 연결", dl_ok,
          [d["concept_name"] for d in dialects if d["node"] not in by_id])
    broken = (meta or {}).get("broken_references", [])
    check("Broken Node ID / name references = 0", not broken, broken[:10])
    unresolved_hub = [(h["hub"], t) for h in stg["hubs"] for t in h["unresolved_tokens"]]
    check("20_Hubs_Rules Linked Concepts 해석", not unresolved_hub, unresolved_hub, hard=False)

    # ---- summary ----------------------------------------------------------
    traps_total = sum(len(c.get("traps", [])) for c in content.values())
    rules_total = sum(len(c.get("rules", [])) for c in content.values())
    wcc = nx.number_weakly_connected_components(dag)
    summary = {
        "Total source concepts": len(source),
        "Current concepts": len(current),
        "Legacy-only concepts": len(legacy_only),
        "CURATED content": depth.get("CURATED", 0),
        "TEMPLATE content": depth.get("TEMPLATE", 0),
        "Review-needed current concepts": review_cur,
        "Concept Structure DAG nodes": sg.number_of_nodes(),
        "Concept Structure DAG edges": sg.number_of_edges(),
        "Structure Is DAG": is_sdag,
        "Structure orphan nodes": len(s_orphans),
        "Concepts missing from structure DAG": len(s_missing),
        "Current concepts missing from structure DAG": len(cur_missing_structure),
        "Learning DAG nodes": dag.number_of_nodes(),
        "Explicit learning edges": len(explicit),
        "Inferred learning edges": len(inferred),
        "Learning Is DAG": is_ldag,
        "Learning weakly connected components": wcc,
        "Learning WCC incl. stage/cluster anchors": nx.number_weakly_connected_components(lg),
        "Concepts without prerequisite": len(roots),
        "Current concepts missing from learning system": len(cur_missing_learning),
        "Mindmap-gap concepts missing": len(gap_missing),
        "Broken Node ID references": len(broken),
        "Orphan nodes": len(l_orphans) + len(s_orphans),
        "Cycles": len(cycle["learning"]["cycles"]) + len(cycle["structure"]["cycles"]),
        "Definitions loaded": len(src_ids) - len(no_def),
        "Rules loaded": rules_total,
        "Exam traps loaded": traps_total,
        "Comparison cards loaded": len(comps),
        "SQL examples loaded": len(examples),
        "Dialect notes loaded": len(dialects),
    }
    details = {
        "learning_dag_node_breakdown": {
            "source_concepts": len(source),
            "dialect_reference_nodes": sum(n["node_type"] == "DIALECT" for n in nodes),
            "curated_structure_nodes": sum(n["synthetic"] and n.get("synthetic_kind") == "structure" for n in nodes),
            "curated_integration_nodes": sum(n["synthetic"] and n.get("synthetic_kind") == "integration" for n in nodes),
        },
        "explicit_learning_edges_by_provenance": dict(Counter(p for e in explicit for p in e["provenance"])),
        "inferred_learning_edges_by_confidence": dict(Counter(e["confidence"] for e in inferred)),
        "structure_edges_by_relation": dict(Counter(r for e in sedges for r in e["relations"])),
        "structure_inferred_edges": sum(e["inferred"] for e in sedges),
        "excluded_explicit_edges": (meta or {}).get("excluded_explicit_edges", []),
        "curated_edges_skipped_as_implied_by_explicit": len((meta or {}).get("curated_edges_skipped_as_implied", [])),
        "curated_edges_duplicating_explicit": len((meta or {}).get("curated_edges_duplicating_explicit", [])),
        "curated_edges_rejected_conflict_with_source": (meta or {}).get("curated_edges_rejected_conflict", []),
        "name_aliases": inf["name_aliases"],
        "inferred_placements": len(inf["placements"]),
        "legacy_only_shown_by_default_as_support(Priority C)": sum(n["visible_by_default"] for n in legacy_only),
        "legacy_only_hidden_by_default": sum(not n["visible_by_default"] for n in legacy_only),
        "default_visible_nodes": sum(n["visible_by_default"] for n in nodes),
        "default_learning_core_nodes": sum(n["visible_by_default"] and n["display_tier"] == "core" for n in nodes),
        "default_structure_core_nodes": sum(n["visible_by_default"] and n["structure_tier"] == "core" for n in nodes),
        "priority_distribution": dict(Counter(n["priority"] for n in nodes)),
        "priority_distribution_current_concepts": dict(Counter(n["priority"] for n in current)),
        "rule_types": dict(Counter(r["type"] for r in rules.values())),
        "example_types": dict(Counter(e["type"] for e in examples)),
        "content_depth_current": dict(Counter(content[n["id"]]["content_depth"] for n in current)),
        "content_coverage_kpi_26": kpi,
        "per_stage": [{"stage": x["stage"], "title": x["title"], "concepts": x["concept_count"],
                       "current": x["current_count"], "default_visible": x["default_visible_count"]} for x in stages],
        "build_notes": (meta or {}).get("notes", []),
    }
    ok = all(c["ok"] for c in checks if c["severity"] == "error")
    return {"ok": ok, "summary": summary, "details": details, "checks": checks}, ok


def print_summary(report: dict) -> None:
    print()
    for k, v in report["summary"].items():
        print(f"{k}: {v}")
    d = report["details"]
    print()
    print("  (explicit learning edges by provenance: "
          + ", ".join(f"{k}={v}" for k, v in d["explicit_learning_edges_by_provenance"].items()) + ")")
    print(f"  (inferred learning edges by confidence: {d['inferred_learning_edges_by_confidence']}; "
          f"curated edges skipped as implied by explicit: {d['curated_edges_skipped_as_implied_by_explicit']})")
    print(f"  (Legacy-only shown as support / hidden by default: "
          f"{d['legacy_only_shown_by_default_as_support(Priority C)']} / {d['legacy_only_hidden_by_default']})")
    print(f"  (Priority distribution: {d['priority_distribution']})")
    failed = [c for c in report["checks"] if not c["ok"]]
    print()
    if not failed:
        print(f"All {len(report['checks'])} validation checks passed.")
    for c in failed:
        print(f"[{c['severity'].upper()}] {c['check']}: {c['detail']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=DATA)
    ap.add_argument("--write", action="store_true", help="rewrite data/validation_report.json")
    args = ap.parse_args()
    meta = None
    rep_path = args.data / "validation_report.json"
    report, ok = validate(args.data, meta=meta)
    if args.write:
        rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print_summary(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
