"""Pipeline / data tests (stdlib unittest; needs networkx + openpyxl like the build).

Run:  python3 -m unittest discover -s tests -v      (from sqld-learning-dag/)
"""

import json
import sys
import unittest
import warnings
from pathlib import Path

import networkx as nx
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_learning_graph as B  # noqa: E402
import validate_graph as V  # noqa: E402

FORBIDDEN = {"CONTRASTS", "AFFECTS", "DIALECT", "DIALECT_OF", "DIALECT_EQUIVALENT", "EXCEPTION",
             "RELATED_TO", "CO_OCCURS_WITH"}


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = B.build(B.DEFAULT_XLSX)
        cls.g = cls.out["_graphs"]
        cls.nodes = {n["id"]: n for n in cls.out["nodes"]}
        cls.by_name = {n["name"]: n for n in cls.out["nodes"]}
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
        wb = openpyxl.load_workbook(B.DEFAULT_XLSX, read_only=True, data_only=True)
        rows = list(wb["21_Concept_Content"].iter_rows(values_only=True))
        head = rows[0]
        cls.content_rows = {r[0]: dict(zip(head, r)) for r in rows[1:] if r[0]}
        wb.close()

    # ---- Excel parsing / identity ------------------------------------------
    def test_excel_parsing_counts(self):
        self.assertEqual(len(self.content_rows), 475)
        self.assertEqual(len(self.out["rules_and_traps"]), 555)
        self.assertEqual(len(self.out["comparisons"]), 24)
        self.assertEqual(len(self.out["examples"]), 65)
        self.assertEqual(len(self.out["dialects"]), 17)
        self.assertEqual(self.out["meta"]["total_source_concepts"], 475)

    def test_node_id_unique_and_canonical(self):
        ids = [n["id"] for n in self.out["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        for nid, row in self.content_rows.items():
            self.assertIn(nid, self.nodes)
            self.assertEqual(self.nodes[nid]["name"], row["Concept"])

    def test_duplicate_concept_mapping(self):
        names = [n["name"] for n in self.out["nodes"]]
        self.assertEqual(len(names), len(set(names)))

    def test_no_broken_references(self):
        self.assertEqual(self.out["meta"]["broken_references"], [])
        for e in self.out["learning_edges"]:
            self.assertIn(e["source"], self.nodes)
            self.assertIn(e["target"], self.nodes)

    # ---- DAGs ---------------------------------------------------------------
    def test_structure_dag_is_acyclic_and_complete(self):
        sg = self.g["structure"]
        self.assertTrue(nx.is_directed_acyclic_graph(sg))
        reach = nx.descendants(sg, self.g["root_id"])
        self.assertTrue(all(nid in reach for nid in self.nodes))

    def test_learning_dag_is_acyclic(self):
        self.assertTrue(nx.is_directed_acyclic_graph(self.g["dag"]))
        self.assertTrue(nx.is_directed_acyclic_graph(self.g["learning"]))

    def test_cycles_are_reported_not_hidden(self):
        pre = self.out["cycle_report"]["learning"]["pre_review_candidate_graph"]
        self.assertFalse(pre["is_dag"])
        excluded = {(x["source_name"], x["target_name"]) for x in self.out["meta"]["excluded_explicit_edges"]}
        self.assertIn(("HAVING", "SELECT"), excluded)
        self.assertFalse(self.g["dag"].has_edge(self.by_name["HAVING"]["id"], self.by_name["SELECT"]["id"]))

    def test_no_forbidden_relation_in_either_dag(self):
        for e in self.out["learning_edges"]:
            self.assertNotIn(e["relation"], FORBIDDEN)
        for e in self.out["structure_edges"]:
            self.assertFalse(set(e["relations"]) & FORBIDDEN)

    def test_explicit_edges_come_from_source(self):
        explicit = [e for e in self.out["learning_edges"] if not e["inferred"]]
        allowed = {"21_Concept_Content.Prerequisites", "17_KG_Edges:REQUIRES", "17_KG_Edges:PRECEDES",
                   "17_KG_Edges:ENABLES", "17_KG_Edges:EXPLAINS"}
        for e in explicit:
            self.assertTrue(set(e["provenance"]) <= allowed, e)

    def test_inferred_edges_have_reason_and_confidence(self):
        for e in self.out["inferred_edges"]:
            self.assertTrue(e["inferred"])
            self.assertTrue(e["reason"])
            self.assertIn(e["confidence"], {"high", "medium", "low"})

    # ---- coverage -----------------------------------------------------------
    def test_current_concepts_covered(self):
        current = [n for n in self.out["nodes"] if n["evidence_status"] == "current"]
        self.assertEqual(len(current), 286)
        reach = nx.descendants(self.g["structure"], self.g["root_id"])
        for n in current:
            self.assertIn(n["id"], reach)
            self.assertTrue(n["visible_by_default"])

    def test_mindmap_gap_covered(self):
        gap = [n for n in self.out["nodes"] if n["mindmap_gap"]]
        self.assertEqual(len(gap), 191)
        self.assertTrue(all(n["visible_by_default"] for n in gap))

    def test_legacy_preserved_and_hidden(self):
        legacy = [n for n in self.out["nodes"] if n["in_legacy_only"]]
        self.assertEqual(len(legacy), 185)
        for name in ("실행계획", "인덱스", "PL/SQL", "분산 데이터베이스", "NESTED LOOP JOIN", "Sort Merge Join",
                     "HASH JOIN", "성능 데이터 모델링", "비용 기반 옵티마이저"):
            n = self.by_name[name]
            self.assertTrue(n["is_legacy"], name)
            self.assertFalse(n["visible_by_default"], name)

    # ---- learning content ---------------------------------------------------
    def test_content_comes_from_workbook(self):
        for nid, row in self.content_rows.items():
            c = self.out["content"][nid]
            self.assertEqual(c["source"], "21_Concept_Content")
            self.assertEqual(c["definition"], (row["Definition"] or "").strip())
            self.assertEqual(c["content_depth"], row["Content Depth"])
            self.assertEqual(c["review_flag"], row["Review Flag"])

    def test_rules_and_traps_linked(self):
        linked = [r for c in self.out["content"].values() for r in c["rules"] + c["traps"]]
        self.assertEqual(sorted(linked), sorted(self.out["rules_and_traps"]))
        traps = self.out["content"][self.by_name["NOT IN"]["id"]]["traps"]
        self.assertTrue(traps)
        self.assertTrue(all(self.out["rules_and_traps"][t]["type"] == "EXAM_TRAP" for t in traps))

    def test_comparisons_linked(self):
        rank = self.out["content"][self.by_name["RANK"]["id"]]
        dense = self.out["content"][self.by_name["DENSE_RANK"]["id"]]
        self.assertIn("C001", rank["comparisons"])
        self.assertIn("C001", dense["comparisons"])
        self.assertFalse(self.g["dag"].has_edge(self.by_name["RANK"]["id"], self.by_name["DENSE_RANK"]["id"]))
        self.assertFalse(self.g["dag"].has_edge(self.by_name["DENSE_RANK"]["id"], self.by_name["RANK"]["id"]))

    def test_examples_linked(self):
        ex = {e["id"]: e for e in self.out["examples"]}
        rank = self.out["content"][self.by_name["RANK"]["id"]]
        result = [ex[x] for x in rank["examples"] if ex[x]["type"] == "RESULT"]
        self.assertTrue(result)
        self.assertEqual(result[0]["expected_result"], "1,2,2,4")

    def test_dialects_linked(self):
        dl = {d["id"]: d for d in self.out["dialects"]}
        self.assertTrue(all(d["node"] in self.nodes for d in dl.values()))
        nvl = self.out["content"][self.by_name["NVL"]["id"]]["dialects"]
        self.assertIn("D004", nvl)
        self.assertIn("D005", nvl)  # ISNULL → NVL alias (recorded as inferred)
        self.assertEqual(self.out["inferred_items"]["name_aliases"][0]["name"], "ISNULL")

    def test_priority_not_from_degree(self):
        for n in self.out["nodes"]:
            self.assertIn(n["priority"], {"A", "B", "C", "Legacy"})
            if n["evidence_status"] == "current" and n["current_rounds"] < 2:
                self.assertEqual(n["priority"], "B", n["name"])


class GeneratedDataTest(unittest.TestCase):
    """Validates the committed data/*.json (what the web app loads)."""

    def test_validation_report_passes(self):
        meta = None
        report_path = ROOT / "data" / "validation_report.json"
        if report_path.exists():
            meta = {"broken_references": []}
        report, ok = V.validate(ROOT / "data", meta=meta)
        failed = [c for c in report["checks"] if not c["ok"] and c["severity"] == "error"]
        self.assertTrue(ok, failed)
        self.assertEqual(report["summary"]["Current concepts missing from structure DAG"], 0)
        self.assertEqual(report["summary"]["Current concepts missing from learning system"], 0)
        self.assertEqual(report["summary"]["Mindmap-gap concepts missing"], 0)

    def test_bundle_matches_data(self):
        text = (ROOT / "web" / "data.js").read_text(encoding="utf-8")
        bundle = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
        nodes = json.loads((ROOT / "data" / "nodes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(bundle["nodes"]), len(nodes))
        self.assertEqual(len(bundle["learning_edges"]),
                         len(json.loads((ROOT / "data" / "prerequisite_edges.json").read_text(encoding="utf-8"))))


if __name__ == "__main__":
    unittest.main()
