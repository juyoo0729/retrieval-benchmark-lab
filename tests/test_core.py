import json
import math
import tempfile
import unittest
from pathlib import Path
from retrieval_lab.metrics import score, percentile
from retrieval_lab.data import load_dataset
from retrieval_lab.retrievers import BM25
from retrieval_lab.cli import evaluate, main


class MetricsTests(unittest.TestCase):
    def test_hand_calculated_multi_gold(self):
        actual = score(["x", "a", "b"], {"a", "b"}, 3)
        self.assertEqual(actual["recall@3"], 1)
        self.assertEqual(actual["mrr@3"], .5)
        expected = (1 / math.log2(3) + .5) / (1 + 1 / math.log2(3))
        self.assertAlmostEqual(actual["ndcg@3"], expected)

    def test_cutoff_and_missing(self):
        self.assertEqual(score(["x", "a"], {"a", "b"}, 1)["recall@1"], 0)
        self.assertEqual(score(["a"], {"a", "b"}, 5)["recall@5"], .5)
        self.assertEqual(score([], {"a"}, 5)["mrr@5"], 0)

    def test_invalid_gold_and_duplicate_ranking(self):
        with self.assertRaises(ValueError):
            score(["a"], set(), 5)
        with self.assertRaises(ValueError):
            score(["a", "a"], {"a"}, 5)

    def test_percentile(self):
        self.assertEqual(percentile([10, 20], .95), 19.5)
        self.assertEqual(percentile([7], .95), 7)


class PipelineTests(unittest.TestCase):
    def test_dataset_split(self):
        docs, queries = load_dataset("data")
        self.assertEqual(len(queries), 34)
        dev = {q["topic"] for q in queries if q["split"] == "dev"}
        test = {q["topic"] for q in queries if q["split"] == "test"}
        self.assertFalse(dev & test)
        self.assertGreater(len(docs), 30)

    def test_unknown_gold_rejected(self):
        docs, queries = load_dataset("data")
        queries[0]["relevant_ids"] = ["unknown"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, rows in [("corpus", docs), ("queries", queries)]:
                (root / (name + ".jsonl")).write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_dataset(root)

    def test_bm25_tie_and_no_overlap(self):
        search = BM25([{"id": "b", "text": "서울 고용"}, {"id": "a", "text": "서울 고용"}])
        self.assertEqual([d for d, _ in search.search("서울", 2)], ["a", "b"])
        self.assertEqual(search.search("zzzz", 2), [])

    def test_errors_remain_in_denominator(self):
        class Broken:
            def search(self, text, limit):
                raise RuntimeError("simulated outage")
        queries = [{"id": "q", "text": "x", "category": "test", "answerable": True, "relevant_ids": ["a"]}]
        summary, rows = evaluate(Broken(), queries, 5)
        self.assertEqual(summary["errors"], 1)
        self.assertEqual(summary["recall@5"], 0)
        self.assertIsNone(summary["p95_ms"])
        self.assertEqual(rows[0]["status"], "error")

    def test_unanswerable_not_in_recall(self):
        class Fixed:
            def search(self, text, limit):
                return [("a", 1)]
        queries = [
            {"id": "q", "text": "x", "category": "test", "answerable": True, "relevant_ids": ["a"]},
            {"id": "u", "text": "y", "category": "test", "answerable": False, "relevant_ids": []},
        ]
        summary, _ = evaluate(Fixed(), queries, 5)
        self.assertEqual(summary["recall@5"], 1)
        self.assertEqual(summary["unanswerable_with_results"], 1)

    def test_cli_report_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(main(["--output", tmp]), 0)
            result = json.loads((Path(tmp) / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(result["config"]["split"], "dev")
            self.assertEqual(len(result["dataset_sha256"]), 64)
            self.assertTrue((Path(tmp) / "report.md").exists())
            with self.assertRaises(SystemExit):
                main(["--output", tmp])


if __name__ == "__main__":
    unittest.main()
