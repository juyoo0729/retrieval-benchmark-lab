# Retrieval benchmark results

**Synthetic internal fixture. Not official statistics or independent evaluation.**

Split: dev / dataset SHA256: a944b390f077fed4fa663fe7e6e00aa20a11a32e23e802918a1eb4b2e34441e2

Latency excludes model loading/corpus indexing; rerank latency includes dense candidate retrieval.
Errors count as zero in answerable-query metrics. No calibrated abstention policy is implemented.

| Method | Recall@5 | MRR@5 | nDCG@5 | p50 ms | p95 ms | Errors |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 1.0000 | 0.8958 | 0.9218 | 0.5901 | 0.7876 | 0 |

## bm25: failures and unanswerable queries

- q02 [paraphrase] 2024년 서울에서 일자리를 구하지만 취업하지 못한 청년 비중 확인할 자료는? — gold=['unemployment-seoul24'], retrieved=['unemployment-confound', 'unemployment-seoul24', 'unemployment-busan24', 'unemployment-seoul23', 'migration-seoul24'], status=ok
- q05 [paraphrase] 2024년 서울에서 일하는 사람이 전체 인구에서 차지하는 비중 확인할 자료는? — gold=['employment-seoul24'], retrieved=['migration-seoul24', 'migration-busan24', 'migration-seoul23', 'employment-seoul24', 'unemployment-seoul24'], status=ok
- q31 [unanswerable] 2035년 제주 청년 실업률 확정 통계를 찾아줘. — gold=[], retrieved=['unemployment-busan24', 'unemployment-seoul23', 'unemployment-seoul24', 'unemployment-confound', 'housing-confound'], status=ok
- q32 [unanswerable] 화성 식민지의 주민등록 인구 통계가 필요해. — gold=[], retrieved=['population-busan24', 'population-seoul23', 'population-seoul24', 'aging-busan24', 'aging-seoul23'], status=ok

