# Retrieval benchmark results

**Synthetic internal fixture. Not official statistics or independent evaluation.**

Split: test / dataset SHA256: 3fe87993aaa63b44e1c7aa9ef7261fe7f0028c7522d9ed41c664dcad686776e3

Latency excludes model loading/corpus indexing; rerank latency includes dense candidate retrieval.
Errors count as zero in answerable-query metrics. No calibrated abstention policy is implemented.

| Method | Recall@5 | MRR@5 | nDCG@5 | p50 ms | p95 ms | Errors |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.8889 | 0.8611 | 0.8684 | 0.6186 | 0.8389 | 0 |
| dense | 0.8333 | 0.6352 | 0.6482 | 18.6959 | 19.5878 | 0 |
| rerank | 0.8611 | 1.0000 | 0.8925 | 288.8908 | 301.7474 | 0 |

## bm25: failures and unanswerable queries

- q17 [paraphrase] 2024년 서울에서 65살 이상 주민이 차지하는 비중 확인할 자료는? — gold=['aging-seoul24'], retrieved=['employment-seoul24', 'employment-busan24', 'employment-seoul23', 'unemployment-seoul24', 'unemployment-busan24'], status=ok
- q23 [paraphrase] 2024년 서울에서 가구 수에 비해 집이 얼마나 공급되어 있는지 확인할 자료는? — gold=['housing-seoul24'], retrieved=['household-seoul24', 'income-seoul24', 'household-busan24', 'household-seoul23', 'income-busan24'], status=ok
- q29 [paraphrase] 2024년 서울에서 들어온 사람에서 떠난 사람을 뺀 인원 확인할 자료는? — gold=['migration-seoul24'], retrieved=['population-seoul24', 'migration-seoul24', 'population-busan24', 'population-seoul23', 'migration-busan24'], status=ok
- q33 [unanswerable] 2024년 서울 고령 인구 비율을 동별로 알려줘. — gold=[], retrieved=['aging-seoul24', 'aging-seoul23', 'aging-busan24', 'aging-confound', 'employment-seoul24'], status=ok
- q34 [unanswerable] 2024년 부산 가구 월평균 소득을 월별로 찾아줘. — gold=[], retrieved=['income-busan24', 'income-seoul24', 'income-seoul23', 'income-confound', 'household-busan24'], status=ok

## dense: failures and unanswerable queries

- q13 [exact] 2024년 서울의 합계출산율 자료를 찾아줘. — gold=['birth-seoul24'], retrieved=['price-seoul24', 'birth-seoul24', 'income-seoul24', 'household-seoul24', 'aging-confound'], status=ok
- q15 [multi_gold_year] 서울 합계출산율의 2023년과 2024년 자료를 함께 찾아줘. — gold=['birth-seoul23', 'birth-seoul24'], retrieved=['price-seoul24', 'birth-seoul24', 'household-seoul24', 'employment-seoul24', 'income-seoul24'], status=ok
- q22 [exact] 2024년 서울의 주택 보급률 자료를 찾아줘. — gold=['housing-seoul24'], retrieved=['household-seoul24', 'housing-seoul24', 'price-seoul24', 'housing-seoul23', 'migration-seoul24'], status=ok
- q23 [paraphrase] 2024년 서울에서 가구 수에 비해 집이 얼마나 공급되어 있는지 확인할 자료는? — gold=['housing-seoul24'], retrieved=['household-seoul24', 'housing-seoul24', 'price-seoul24', 'migration-seoul24', 'housing-seoul23'], status=ok
- q24 [multi_gold_year] 서울 주택 보급률의 2023년과 2024년 자료를 함께 찾아줘. — gold=['housing-seoul23', 'housing-seoul24'], retrieved=['household-seoul24', 'housing-seoul24', 'price-seoul24', 'housing-seoul23', 'migration-seoul24'], status=ok
- q25 [exact] 2024년 서울의 가구 월평균 소득 자료를 찾아줘. — gold=['income-seoul24'], retrieved=['price-seoul24', 'employment-seoul24', 'birth-seoul24', 'household-seoul24', 'income-seoul24'], status=ok
- q26 [paraphrase] 2024년 서울에서 한 집이 한 달에 평균적으로 버는 돈 확인할 자료는? — gold=['income-seoul24'], retrieved=['household-seoul24', 'price-seoul24', 'income-seoul24', 'employment-seoul24', 'birth-seoul24'], status=ok
- q27 [multi_gold_year] 서울 가구 월평균 소득의 2023년과 2024년 자료를 함께 찾아줘. — gold=['income-seoul23', 'income-seoul24'], retrieved=['price-seoul24', 'employment-seoul24', 'birth-seoul24', 'household-seoul24', 'income-seoul24'], status=ok
- q28 [exact] 2024년 서울의 순이동 인구 자료를 찾아줘. — gold=['migration-seoul24'], retrieved=['price-seoul24', 'aging-seoul24', 'household-seoul24', 'birth-seoul24', 'migration-seoul24'], status=ok
- q30 [multi_gold_year] 서울 순이동 인구의 2023년과 2024년 자료를 함께 찾아줘. — gold=['migration-seoul23', 'migration-seoul24'], retrieved=['price-seoul24', 'aging-seoul24', 'birth-seoul24', 'employment-seoul24', 'household-seoul24'], status=ok
- q33 [unanswerable] 2024년 서울 고령 인구 비율을 동별로 알려줘. — gold=[], retrieved=['aging-seoul24', 'employment-seoul24', 'price-seoul24', 'birth-seoul24', 'household-seoul24'], status=ok
- q34 [unanswerable] 2024년 부산 가구 월평균 소득을 월별로 찾아줘. — gold=[], retrieved=['income-seoul24', 'employment-seoul24', 'household-seoul24', 'aging-seoul24', 'migration-seoul24'], status=ok

## rerank: failures and unanswerable queries

- q33 [unanswerable] 2024년 서울 고령 인구 비율을 동별로 알려줘. — gold=[], retrieved=['aging-seoul24', 'household-seoul24', 'aging-confound', 'migration-seoul24', 'employment-seoul24'], status=ok
- q34 [unanswerable] 2024년 부산 가구 월평균 소득을 월별로 찾아줘. — gold=[], retrieved=['income-seoul24', 'income-seoul23', 'household-busan24', 'aging-busan24', 'household-seoul24'], status=ok

