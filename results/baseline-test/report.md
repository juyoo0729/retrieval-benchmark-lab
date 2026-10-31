# Retrieval benchmark results

**Synthetic internal fixture. Not official statistics or independent evaluation.**

Split: test / dataset SHA256: a944b390f077fed4fa663fe7e6e00aa20a11a32e23e802918a1eb4b2e34441e2

Latency excludes model loading/corpus indexing; rerank latency includes dense candidate retrieval.
Errors count as zero in answerable-query metrics. No calibrated abstention policy is implemented.

| Method | Recall@5 | MRR@5 | nDCG@5 | p50 ms | p95 ms | Errors |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.8889 | 0.8611 | 0.8684 | 0.6324 | 0.9852 | 0 |

## bm25: failures and unanswerable queries

- q17 [paraphrase] 2024년 서울에서 65살 이상 주민이 차지하는 비중 확인할 자료는? — gold=['aging-seoul24'], retrieved=['employment-seoul24', 'employment-busan24', 'employment-seoul23', 'unemployment-seoul24', 'unemployment-busan24'], status=ok
- q23 [paraphrase] 2024년 서울에서 가구 수에 비해 집이 얼마나 공급되어 있는지 확인할 자료는? — gold=['housing-seoul24'], retrieved=['household-seoul24', 'income-seoul24', 'household-busan24', 'household-seoul23', 'income-busan24'], status=ok
- q29 [paraphrase] 2024년 서울에서 들어온 사람에서 떠난 사람을 뺀 인원 확인할 자료는? — gold=['migration-seoul24'], retrieved=['population-seoul24', 'migration-seoul24', 'population-busan24', 'population-seoul23', 'migration-busan24'], status=ok
- q33 [unanswerable] 2024년 서울 고령 인구 비율을 동별로 알려줘. — gold=[], retrieved=['aging-seoul24', 'aging-seoul23', 'aging-busan24', 'aging-confound', 'employment-seoul24'], status=ok
- q34 [unanswerable] 2024년 부산 가구 월평균 소득을 월별로 찾아줘. — gold=[], retrieved=['income-busan24', 'income-seoul24', 'income-seoul23', 'income-confound', 'household-busan24'], status=ok

