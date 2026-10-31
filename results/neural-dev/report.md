# Retrieval benchmark results

**Synthetic internal fixture. Not official statistics or independent evaluation.**

Split: dev / dataset SHA256: 3fe87993aaa63b44e1c7aa9ef7261fe7f0028c7522d9ed41c664dcad686776e3

Latency excludes model loading/corpus indexing; rerank latency includes dense candidate retrieval.
Errors count as zero in answerable-query metrics. No calibrated abstention policy is implemented.

| Method | Recall@5 | MRR@5 | nDCG@5 | p50 ms | p95 ms | Errors |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 1.0000 | 0.8958 | 0.9218 | 0.5723 | 0.8158 | 0 |
| dense | 0.6250 | 0.5417 | 0.5233 | 17.8036 | 18.9013 | 0 |
| rerank | 0.6250 | 0.6944 | 0.6116 | 286.2478 | 298.6738 | 0 |

## bm25: failures and unanswerable queries

- q02 [paraphrase] 2024년 서울에서 일자리를 구하지만 취업하지 못한 청년 비중 확인할 자료는? — gold=['unemployment-seoul24'], retrieved=['unemployment-confound', 'unemployment-seoul24', 'unemployment-busan24', 'unemployment-seoul23', 'migration-seoul24'], status=ok
- q05 [paraphrase] 2024년 서울에서 일하는 사람이 전체 인구에서 차지하는 비중 확인할 자료는? — gold=['employment-seoul24'], retrieved=['migration-seoul24', 'migration-busan24', 'migration-seoul23', 'employment-seoul24', 'unemployment-seoul24'], status=ok
- q31 [unanswerable] 2035년 제주 청년 실업률 확정 통계를 찾아줘. — gold=[], retrieved=['unemployment-busan24', 'unemployment-seoul23', 'unemployment-seoul24', 'unemployment-confound', 'housing-confound'], status=ok
- q32 [unanswerable] 화성 식민지의 주민등록 인구 통계가 필요해. — gold=[], retrieved=['population-busan24', 'population-seoul23', 'population-seoul24', 'aging-busan24', 'aging-seoul23'], status=ok

## dense: failures and unanswerable queries

- q01 [exact] 2024년 서울의 청년 실업률 자료를 찾아줘. — gold=['unemployment-seoul24'], retrieved=['employment-seoul24', 'unemployment-seoul24', 'price-seoul24', 'household-seoul24', 'income-seoul24'], status=ok
- q02 [paraphrase] 2024년 서울에서 일자리를 구하지만 취업하지 못한 청년 비중 확인할 자료는? — gold=['unemployment-seoul24'], retrieved=['employment-seoul24', 'unemployment-seoul24', 'price-seoul24', 'income-seoul24', 'household-seoul24'], status=ok
- q03 [multi_gold_year] 서울 청년 실업률의 2023년과 2024년 자료를 함께 찾아줘. — gold=['unemployment-seoul23', 'unemployment-seoul24'], retrieved=['employment-seoul24', 'unemployment-seoul24', 'price-seoul24', 'birth-seoul24', 'income-seoul24'], status=ok
- q04 [exact] 2024년 서울의 고용률 자료를 찾아줘. — gold=['employment-seoul24'], retrieved=['price-seoul24', 'employment-seoul24', 'unemployment-seoul24', 'birth-seoul24', 'income-seoul24'], status=ok
- q06 [multi_gold_year] 서울 고용률의 2023년과 2024년 자료를 함께 찾아줘. — gold=['employment-seoul23', 'employment-seoul24'], retrieved=['price-seoul24', 'employment-seoul24', 'birth-seoul24', 'unemployment-seoul24', 'income-seoul24'], status=ok
- q07 [exact] 2024년 서울의 주민등록 인구 자료를 찾아줘. — gold=['population-seoul24'], retrieved=['price-seoul24', 'household-seoul24', 'migration-seoul24', 'aging-seoul24', 'birth-seoul24'], status=ok
- q08 [paraphrase] 2024년 서울에서 주민으로 등록된 사람은 몇 명인지 확인할 자료는? — gold=['population-seoul24'], retrieved=['household-seoul24', 'price-seoul24', 'aging-seoul24', 'employment-seoul24', 'migration-seoul24'], status=ok
- q09 [multi_gold_year] 서울 주민등록 인구의 2023년과 2024년 자료를 함께 찾아줘. — gold=['population-seoul23', 'population-seoul24'], retrieved=['aging-seoul24', 'price-seoul24', 'birth-seoul24', 'migration-seoul24', 'employment-seoul24'], status=ok
- q31 [unanswerable] 2035년 제주 청년 실업률 확정 통계를 찾아줘. — gold=[], retrieved=['income-busan24', 'population-busan24', 'birth-busan24', 'income-seoul23', 'migration-busan24'], status=ok
- q32 [unanswerable] 화성 식민지의 주민등록 인구 통계가 필요해. — gold=[], retrieved=['migration-seoul24', 'aging-seoul23', 'aging-busan24', 'aging-seoul24', 'migration-seoul23'], status=ok

## rerank: failures and unanswerable queries

- q05 [paraphrase] 2024년 서울에서 일하는 사람이 전체 인구에서 차지하는 비중 확인할 자료는? — gold=['employment-seoul24'], retrieved=['aging-seoul24', 'household-seoul24', 'employment-seoul24', 'unemployment-seoul24', 'migration-seoul24'], status=ok
- q07 [exact] 2024년 서울의 주민등록 인구 자료를 찾아줘. — gold=['population-seoul24'], retrieved=['aging-confound', 'migration-seoul24', 'aging-seoul24', 'household-seoul24', 'income-confound'], status=ok
- q08 [paraphrase] 2024년 서울에서 주민으로 등록된 사람은 몇 명인지 확인할 자료는? — gold=['population-seoul24'], retrieved=['migration-seoul24', 'aging-seoul24', 'household-seoul24', 'aging-confound', 'birth-seoul24'], status=ok
- q09 [multi_gold_year] 서울 주민등록 인구의 2023년과 2024년 자료를 함께 찾아줘. — gold=['population-seoul23', 'population-seoul24'], retrieved=['migration-seoul23', 'aging-confound', 'aging-seoul24', 'migration-seoul24', 'household-seoul24'], status=ok
- q31 [unanswerable] 2035년 제주 청년 실업률 확정 통계를 찾아줘. — gold=[], retrieved=['birth-seoul23', 'income-seoul23', 'birth-busan24', 'income-seoul24', 'income-busan24'], status=ok
- q32 [unanswerable] 화성 식민지의 주민등록 인구 통계가 필요해. — gold=[], retrieved=['household-seoul24', 'household-seoul23', 'aging-seoul24', 'aging-seoul23', 'migration-seoul24'], status=ok

