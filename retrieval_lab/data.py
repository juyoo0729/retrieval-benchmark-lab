import json
from pathlib import Path


def load_dataset(directory):
    directory = Path(directory)
    docs = [json.loads(line) for line in (directory / "corpus.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    queries = [json.loads(line) for line in (directory / "queries.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not docs or not queries:
        raise ValueError("Corpus and queries must not be empty")
    for rows in (docs, queries):
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate IDs in dataset")
        if any(not isinstance(row["text"], str) or not row["text"].strip() for row in rows):
            raise ValueError("Blank document/query text")
    doc_ids = {doc["id"] for doc in docs}
    texts = set()
    for query in queries:
        if query["split"] not in {"dev", "test"}:
            raise ValueError("split must be dev or test")
        normalized = " ".join(query["text"].split()).casefold()
        if normalized in texts:
            raise ValueError("Duplicate query text (possible split leakage)")
        texts.add(normalized)
        gold = query["relevant_ids"]
        if len(gold) != len(set(gold)) or not set(gold) <= doc_ids:
            raise ValueError("Duplicate or unknown relevant IDs")
        if query["answerable"] != bool(gold):
            raise ValueError("answerable and relevant_ids disagree")
    return docs, queries
