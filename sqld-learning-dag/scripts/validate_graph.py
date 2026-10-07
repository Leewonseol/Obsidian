#!/usr/bin/env python3
"""Validate the generated Learning DAG data (data/*.json).

Run standalone after a build:   python3 scripts/validate_graph.py [--write]
The build script also calls validate() and writes data/validation_report.json.

The graph is rebuilt from the JSON files (not reused from the build) unless the caller passes
`graphs`, so this script is an independent check of what the web app actually loads.
Exit code is non-zero when a hard check fails.
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

ALLOWED_EXPLICIT = {"REQUIRES", "PRECEDES", "ENABLES", "EXPLAINS"}
FORBIDDEN = {"CONTRASTS", "AFFECTS", "DIALECT", "DIALECT_OF", "DIALECT_EQUIVALENT", "EXCEPTION",
             "RELATED_TO", "IS_A", "IMPLEMENTS"}
EXPECTED = {"source_concepts": 475, "current": 286, "legacy_only": 185, "gap": 191}


def load(data_dir: Path, name: str):
    return json.loads((data_dir / name).read_text(encoding="utf-8"))


def stage_order(stage) -> int:
    return 10 if stage == "L" else int(stage)


def validate(data_dir: Path = DATA, graphs: dict | None = None, meta: dict | None = None):
    nodes = load(data_dir, "nodes.json")
    edges = load(data_dir, "prerequisite_edges.json")
    inferred = load(data_dir, "inferred_edges.json")
    hier = load(data_dir, "hierarchy_edges.json")
    rules = load(data_dir, "rules.json")
    comps = load(data_dir, "comparisons.json")
    dials = load(data_dir, "dialects.json")
    stg = load(data_dir, "stages.json")
    legacy = load(data_dir, "legacy_nodes.json")
    cycle = load(data_dir, "cycle_report.json")

    by_id = {n["id"]: n for n in nodes}
    checks = []  # (name, ok, detail, hard)

    def check(name, ok, detail="", hard=True):
        checks.append({"check": name, "ok": bool(ok), "detail": detail, "severity": "error" if hard else "warning"})

    # ---- graphs -----------------------------------------------------------
    dag = nx.DiGraph()
    dag.add_nodes_from(by_id)
    unknown_refs = []
    for e in edges:
        if e["source"] not in by_id or e["target"] not in by_id:
            unknown_refs.append(e)
        dag.add_edge(e["source"], e["target"])
    check("모든 prerequisite edge의 노드가 존재", not unknown_refs, f"{len(unknown_refs)} unknown")

    lg = nx.DiGraph()
    stages = stg["stages"]
    clusters = {c["code"]: c for c in stg["clusters"]}
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

    is_dag = nx.is_directed_acyclic_graph(dag)
    check("networkx.is_directed_acyclic_graph(learning_graph) — Concept prerequisite DAG", is_dag)
    check("Stage/Cluster anchor를 포함한 learning graph도 DAG", nx.is_directed_acyclic_graph(lg))
    check("cycle_report.is_dag와 일치", cycle["is_dag"] == is_dag)

    # ---- edge rules -------------------------------------------------------
    bad_rel = [e for e in edges if e["origin"] == "explicit"
               and (set(e.get("source_relations", [])) - ALLOWED_EXPLICIT)]
    check("명시 prerequisite edge는 REQUIRES/PRECEDES/ENABLES/EXPLAINS만", not bad_rel,
          ", ".join(f"{e['source_name']}→{e['target_name']}" for e in bad_rel))
    forb = [e for e in edges if set(e.get("source_relations", [])) & FORBIDDEN]
    check("CONTRASTS/AFFECTS/DIALECT*/EXCEPTION/IS_A/IMPLEMENTS 관계가 DAG edge로 쓰이지 않음", not forb)
    no_reason = [e for e in inferred if not e.get("inferred") or not str(e.get("reason", "")).strip()]
    check("모든 inferred edge에 inferred:true와 reason 존재", not no_reason, f"{len(no_reason)} missing")
    dup = [k for k, v in Counter((e["source"], e["target"]) for e in edges).items() if v > 1]
    check("중복 prerequisite edge 없음", not dup)
    self_loops = [e for e in edges if e["source"] == e["target"]]
    check("self-loop 없음", not self_loops)

    stage_viol = [f"{e['source_name']}(S{by_id[e['source']]['stage']}) → {e['target_name']}(S{by_id[e['target']]['stage']})"
                  for e in edges if stage_order(by_id[e["source"]]["stage"]) > stage_order(by_id[e["target"]]["stage"])]
    check("Stage 단조성: 선수 Concept의 Stage ≤ 다음 Concept의 Stage", not stage_viol, "; ".join(stage_viol[:20]))

    # ---- coverage ---------------------------------------------------------
    source = [n for n in nodes if not n["synthetic"] and n["node_type"] != "DIALECT"]
    current = [n for n in source if n["evidence_status"] == "current"]
    legacy_only = [n for n in source if n["in_legacy_only"]]
    gap = [n for n in source if n["mindmap_gap"]]
    check("Total source concepts = 475", len(source) == EXPECTED["source_concepts"], str(len(source)))
    check("Current concepts = 286 (10_Current_Evidence)", len(current) == EXPECTED["current"], str(len(current)))
    check("Legacy-only concepts = 185 보존 (11_Legacy_Only)", len(legacy_only) == EXPECTED["legacy_only"] == len(legacy),
          f"{len(legacy_only)} / legacy_nodes.json {len(legacy)}")
    check("Mindmap-gap concepts = 191 (13_Current_Mindmap_Gaps)", len(gap) == EXPECTED["gap"], str(len(gap)))

    reachable = set()
    for x in stages:
        reachable |= nx.descendants(lg, f"STAGE_{x['stage']}")
    orphans = [n["name"] for n in nodes if n["id"] not in reachable]
    check("Orphan concept 없음 (모든 Concept이 Stage root에서 도달 가능)", not orphans, ", ".join(orphans[:20]))

    cur_missing = [n["name"] for n in current if n["id"] not in dag or n["id"] not in reachable]
    cur_hidden = [n["name"] for n in current if not n["visible_by_default"]]
    gap_missing = [n["name"] for n in gap if n["id"] not in dag or n["id"] not in reachable]
    gap_hidden = [n["name"] for n in gap if not n["visible_by_default"]]
    check("Current concepts not included in DAG = 0", not cur_missing, ", ".join(cur_missing))
    check("Current concepts가 기본 화면에서 숨겨지지 않음", not cur_hidden, ", ".join(cur_hidden))
    check("Mindmap-gap concepts not included in DAG = 0", not gap_missing, ", ".join(gap_missing))
    check("Mindmap-gap concepts가 기본 화면에서 숨겨지지 않음", not gap_hidden, ", ".join(gap_hidden))

    # ---- visibility consistency ------------------------------------------
    broken = []
    for n in nodes:
        if n["visible_by_default"]:
            for p in dag.predecessors(n["id"]):
                if not by_id[p]["visible_by_default"]:
                    broken.append(f"{by_id[p]['name']} → {n['name']}")
    check("기본 화면 노드의 선수 노드도 기본 화면에 있음(경로 끊김 없음)", not broken, "; ".join(broken[:20]))
    oos_support = [n["name"] for n in nodes if n.get("legacy_kind") == "out_of_scope" and n["visible_by_default"]]
    check("현행 범위 밖 Legacy(D7 등)는 기본 화면에서 숨김", not oos_support, ", ".join(oos_support))
    legacy_shown = [n for n in legacy_only if n["visible_by_default"]]
    legacy_hidden = [n for n in legacy_only if not n["visible_by_default"]]

    # ---- hierarchy --------------------------------------------------------
    hg = nx.DiGraph([(h["source"], h["target"]) for h in hier])
    check("hierarchy edge 그래프도 cycle 없음", nx.is_directed_acyclic_graph(hg))
    no_cluster = [n["name"] for n in nodes if n["cluster"] not in clusters]
    check("모든 Concept이 Cluster에 배치됨", not no_cluster, ", ".join(no_cluster))

    # ---- content ----------------------------------------------------------
    no_def = [n["name"] for n in nodes if not rules[n["id"]]["definition"]]
    check("모든 노드에 definition 존재", not no_def, ", ".join(no_def[:30]), hard=False)
    a_nodes = [n for n in nodes if n["priority"] == "A"]
    a_no_rule = [n["name"] for n in a_nodes if not rules[n["id"]]["core_rule"] and not rules[n["id"]]["exam_traps"]]
    check("Priority A 노드에 core_rule 또는 exam_traps 존재", not a_no_rule, ", ".join(a_no_rule), hard=False)
    bad_cmp = [c["id"] for c in comps if any(x not in by_id for x in c["concepts"])]
    bad_dl = [d["id"] for d in dials if any(x not in by_id for x in d["concepts"])]
    check("comparison/dialect 카드의 Concept 참조 유효", not bad_cmp and not bad_dl, ", ".join(bad_cmp + bad_dl))
    unresolved_hub = [(h["hub"], t) for h in stg["hubs"] for t in h["unresolved_tokens"]]
    check("20_Hubs_Rules Linked Concepts 해석 완료", not unresolved_hub, str(unresolved_hub), hard=False)

    # ---- structure info ---------------------------------------------------
    redundant = []
    for a, b in list(dag.edges()):
        dag.remove_edge(a, b)
        if nx.has_path(dag, a, b):
            redundant.append(f"{by_id[a]['name']} → {by_id[b]['name']}")
        dag.add_edge(a, b)
    standalone = [n["name"] for n in nodes if dag.in_degree(n["id"]) == 0 and dag.out_degree(n["id"]) == 0]
    wcc_anchor = nx.number_weakly_connected_components(lg)
    wcc_concepts = nx.number_weakly_connected_components(dag)
    check("Stage backbone 포함 learning graph가 단일 weakly connected component", wcc_anchor == 1, str(wcc_anchor))

    explicit_edges = [e for e in edges if e["origin"] == "explicit"]
    summary = {
        "Total source concepts": len(source),
        "Current concepts": len(current),
        "Legacy-only concepts": len(legacy_only),
        "Learning DAG nodes": len(by_id),
        "Explicit prerequisite edges": len(explicit_edges),
        "Inferred prerequisite edges": len(inferred),
        "Hierarchy edges": len(hier),
        "Is DAG": is_dag,
        "Number of weakly connected components": wcc_anchor,
        "Orphan concepts": len(orphans),
        "Current concepts not included in DAG": len(cur_missing),
        "Mindmap-gap concepts not included in DAG": len(gap_missing),
    }
    details = {
        "learning_dag_node_breakdown": {
            "source_concepts": len(source),
            "dialect_reference_nodes": sum(n["node_type"] == "DIALECT" for n in nodes),
            "synthetic_structure_nodes": sum(n["synthetic"] and n.get("synthetic_kind") == "structure" for n in nodes),
            "synthetic_integration_nodes": sum(n["synthetic"] and n.get("synthetic_kind") == "integration" for n in nodes),
        },
        "stage_cluster_anchor_nodes": len(stages) + len(clusters),
        "weakly_connected_components_concept_only_prerequisite_graph": wcc_concepts,
        "standalone_concepts_cluster_root_anchored": {"count": len(standalone), "names": standalone},
        "cluster_root_concepts(no prerequisite)": len(roots),
        "legacy_only_shown_by_default_as_support(Priority C)": len(legacy_shown),
        "legacy_only_hidden_by_default": len(legacy_hidden),
        "default_visible_nodes": sum(n["visible_by_default"] for n in nodes),
        "default_core_tier_nodes": sum(n["visible_by_default"] and n["display_tier"] == "core" for n in nodes),
        "priority_distribution": dict(Counter(n["priority"] for n in nodes)),
        "priority_distribution_current_concepts": dict(Counter(n["priority"] for n in current)),
        "evidence_status_distribution": dict(Counter(n["evidence_status"] for n in nodes)),
        "explicit_edges_by_relation": dict(Counter(r for e in explicit_edges for r in e["source_relations"])),
        "inferred_edges_overlapping_source_relations": dict(Counter(
            r for e in inferred for r in e.get("related_source_relations", []))),
        "transitively_redundant_prerequisite_edges(info)": {"count": len(redundant), "examples": redundant[:15]},
        "max_prerequisite_depth": max(n["depth"] for n in nodes),
        "placement_overrides": [
            {"name": n["name"], **n["placement_override"]} for n in nodes if n.get("placement_override")
        ],
        "nodes_without_definition": no_def,
        "per_stage": [
            {"stage": x["stage"], "title": x["title"], "concepts": x["concept_count"], "current": x["current_count"],
             "default_visible": x["default_visible_count"]} for x in stages
        ],
    }
    if meta:
        details["build_notes"] = meta.get("notes", [])
        details["curated_edges_duplicating_explicit"] = meta.get("curated_edges_duplicating_explicit", [])

    ok = all(c["ok"] for c in checks if c["severity"] == "error")
    report = {"ok": ok, "summary": summary, "details": details, "checks": checks,
              "cycle_report_pre_review": cycle.get("pre_review_candidate_graph", {}).get("resolution", [])}
    return report, ok


def print_summary(report: dict) -> None:
    print()
    for k, v in report["summary"].items():
        print(f"{k}: {v}")
    d = report["details"]
    print()
    print("  (Learning DAG nodes breakdown: "
          + ", ".join(f"{k}={v}" for k, v in d["learning_dag_node_breakdown"].items()) + ")")
    print(f"  (Weakly connected components, concept-only prerequisite graph: "
          f"{d['weakly_connected_components_concept_only_prerequisite_graph']}; "
          f"standalone cluster-root concepts: {d['standalone_concepts_cluster_root_anchored']['count']})")
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
    report, ok = validate(args.data)
    if args.write:
        (args.data / "validation_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print_summary(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
