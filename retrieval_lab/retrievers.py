import math
import re
from collections import Counter


def tokenize(text):
    # Transparent baseline: words + Hangul bigrams, not a morphology analyzer.
    words = re.findall(r"[가-힣]+|[a-z]+|[0-9]+", text.lower())
    grams = ["~" + word[i:i + 2] for word in words if re.fullmatch(r"[가-힣]+", word) for i in range(len(word) - 1)]
    return words + grams


class BM25:
    def __init__(self, docs):
        self.docs = docs
        self.counts = [Counter(tokenize(doc["text"])) for doc in docs]
        self.lengths = [sum(count.values()) for count in self.counts]
        self.average = sum(self.lengths) / len(docs) or 1
        frequency = Counter(token for counts in self.counts for token in counts)
        self.idf = {token: math.log(1 + (len(docs) - count + .5) / (count + .5)) for token, count in frequency.items()}

    def search(self, query, limit):
        scores = []
        for doc, counts, length in zip(self.docs, self.counts, self.lengths):
            value = 0.0
            for token in sorted(set(tokenize(query))):
                tf = counts[token]
                value += self.idf.get(token, 0) * tf * 2.5 / (tf + 1.5 * (.25 + .75 * length / self.average))
            if value > 0:
                scores.append((doc["id"], value))
        return sorted(scores, key=lambda item: (-item[1], item[0]))[:limit]


class Dense:
    def __init__(self, docs, model, revision, device):
        from sentence_transformers import SentenceTransformer
        self.docs = docs
        self.model = SentenceTransformer(model, revision=revision, device=device, trust_remote_code=False)
        self.vectors = self.model.encode([doc["text"] for doc in docs], normalize_embeddings=True, show_progress_bar=False)

    def search(self, query, limit):
        vector = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
        scores = self.vectors @ vector
        return sorted([(doc["id"], float(value)) for doc, value in zip(self.docs, scores)], key=lambda item: (-item[1], item[0]))[:limit]


class Reranker:
    def __init__(self, dense, docs, model, revision, device, candidates):
        from sentence_transformers import CrossEncoder
        self.dense = dense
        self.texts = {doc["id"]: doc["text"] for doc in docs}
        self.candidates = candidates
        self.model = CrossEncoder(model, revision=revision, device=device, trust_remote_code=False)

    def search(self, query, limit):
        candidates = self.dense.search(query, self.candidates)
        if not candidates:
            return []
        scores = self.model.predict([(query, self.texts[doc]) for doc, _ in candidates], show_progress_bar=False)
        return sorted([(doc, float(value)) for (doc, _), value in zip(candidates, scores)], key=lambda item: (-item[1], item[0]))[:limit]
