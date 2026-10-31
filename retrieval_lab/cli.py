import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .data import load_dataset
from .metrics import percentile, score
from .retrievers import BM25, Dense, Reranker

EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


def evaluate(retriever, queries, k):
    rows = []
    for query in queries:
        start = time.perf_counter()
        row = {"query_id": query["id"], "query": query["text"], "category": query["category"],
               "answerable": query["answerable"], "gold": query["relevant_ids"]}
        try:
            ranking = retriever.search(query["text"], k)
            row.update(status="ok", ranked=[doc for doc, _ in ranking],
                       scores=[float(value) for _, value in ranking])
            if query["answerable"]:
                row.update(score(row["ranked"], set(query["relevant_ids"]), k))
        except Exception as exc:
            # Errors remain in the denominator and the run returns nonzero.
            row.update(status="error", error=f"{type(exc).__name__}: {exc}", ranked=[])
            if query["answerable"]:
                row.update(score([], set(query["relevant_ids"]), k))
        row["latency_ms"] = (time.perf_counter() - start) * 1000
        rows.append(row)
    answerable = [r for r in rows if r["answerable"]]
    unanswerable = [r for r in rows if not r["answerable"]]
    summary = {"queries": len(rows), "answerable": len(answerable), "unanswerable": len(unanswerable),
               "errors": sum(r["status"] == "error" for r in rows)}
    for metric in (f"recall@{k}", f"mrr@{k}", f"ndcg@{k}"):
        summary[metric] = sum(r[metric] for r in answerable) / len(answerable) if answerable else None
    successful = [r["latency_ms"] for r in rows if r["status"] == "ok"]
    summary.update(p50_ms=percentile(successful, .5), p95_ms=percentile(successful, .95),
                   unanswerable_with_results=sum(bool(r["ranked"]) for r in unanswerable))
    return summary, rows


def render_report(result):
    k = result["config"]["k"]
    lines = ["# Retrieval benchmark results", "",
             "**Synthetic internal fixture. Not official statistics or independent evaluation.**", "",
             f"Split: {result['config']['split']} / dataset SHA256: {result['dataset_sha256']}", "",
             "Latency excludes model loading/corpus indexing; rerank latency includes dense candidate retrieval.",
             "Errors count as zero in answerable-query metrics. No calibrated abstention policy is implemented.", "",
             f"| Method | Recall@{k} | MRR@{k} | nDCG@{k} | p50 ms | p95 ms | Errors |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    def fmt(value):
        return "N/A" if value is None else f"{value:.4f}"
    for name, run in result["methods"].items():
        s = run["summary"]
        values = [fmt(s[key]) for key in (f"recall@{k}", f"mrr@{k}", f"ndcg@{k}", "p50_ms", "p95_ms")]
        lines.append(f"| {name} | " + " | ".join(values) + f" | {s['errors']} |")
    for name, run in result["methods"].items():
        lines += ["", f"## {name}: failures and unanswerable queries", ""]
        failures = [r for r in run["queries"] if r["status"] == "error" or not r["answerable"] or r.get(f"mrr@{k}", 0) < 1]
        if not failures:
            lines.append("No first-rank misses in this fixture; this does not establish generalization.")
        for row in failures:
            lines.append(f"- {row['query_id']} [{row['category']}] {row['query']} — gold={row['gold']}, retrieved={row['ranked']}, status={row['status']}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Korean retrieval benchmark")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("results/local"))
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--methods", nargs="+", choices=["bm25", "dense", "rerank"], default=["bm25"])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--candidates", type=int, default=10)
    parser.add_argument("--embedding-model", default=EMBEDDING)
    parser.add_argument("--reranker-model", default=RERANKER)
    parser.add_argument("--embedding-revision")
    parser.add_argument("--reranker-revision")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)
    if args.k < 1 or args.candidates < args.k:
        parser.error("Require candidates >= k >= 1")
    docs, all_queries = load_dataset(args.data)
    queries = [q for q in all_queries if q["split"] == args.split]
    if not queries:
        parser.error("Selected split has no queries")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output directory must be empty: preserve earlier experiments")
    digest = hashlib.sha256()
    for name in ("corpus.jsonl", "queries.jsonl"):
        digest.update(name.encode())
        digest.update((args.data / name).read_bytes())
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    result = {"created_at": datetime.now(timezone.utc).isoformat(), "dataset_sha256": digest.hexdigest(),
              "git_commit": commit, "git_dirty": dirty, "python": platform.python_version(),
              "platform": platform.platform(), "processor": platform.processor(),
              "config": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
              "packages": {}, "model_revisions": {}, "methods": {}}
    engines = {}
    if "bm25" in args.methods:
        start = time.perf_counter()
        engines["bm25"] = BM25(docs)
        result["bm25_setup_seconds"] = time.perf_counter() - start
    if any(name in args.methods for name in ("dense", "rerank")):
        try:
            from huggingface_hub import HfApi
            import torch
            torch.manual_seed(0)
            torch.set_num_threads(4)
            result["torch_threads"] = 4
            result["device"] = args.device
            for package in ("sentence-transformers", "transformers", "torch", "numpy", "huggingface-hub"):
                result["packages"][package] = importlib.metadata.version(package)
            start = time.perf_counter()
            revision = HfApi().model_info(args.embedding_model, revision=args.embedding_revision).sha
            result["model_revisions"][args.embedding_model] = revision
            dense = Dense(docs, args.embedding_model, revision, args.device)
            result["dense_setup_seconds"] = time.perf_counter() - start
            engines["dense"] = dense
            if "rerank" in args.methods:
                start = time.perf_counter()
                revision = HfApi().model_info(args.reranker_model, revision=args.reranker_revision).sha
                result["model_revisions"][args.reranker_model] = revision
                engines["rerank"] = Reranker(dense, docs, args.reranker_model, revision, args.device, args.candidates)
                result["rerank_setup_seconds"] = time.perf_counter() - start
        except Exception as exc:
            parser.exit(2, f"Neural initialization failed; no comparison published: {type(exc).__name__}: {exc}\n")
    for name in dict.fromkeys(args.methods):
        # Fixed warmup, not a scored test question.
        engines[name].search("검색 준비", args.k)
        summary, rows = evaluate(engines[name], queries, args.k)
        result["methods"][name] = {"summary": summary, "queries": rows}
        print(name, json.dumps(summary))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output / "report.md").write_text(render_report(result), encoding="utf-8")
    return int(any(run["summary"]["errors"] for run in result["methods"].values()))


if __name__ == "__main__":
    raise SystemExit(main())

