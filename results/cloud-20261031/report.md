# Cloud comparison · 2026-10-31

실행: [GitHub Actions #1](https://github.com/juyoo0729/retrieval-benchmark-lab/actions/runs/41170845618)
코드: `933e9cb776a5bb96d33ca65e7d3129a7d7436b41`
실행 환경: Ubuntu 26.04.1, Python 3.11.17, CPU, torch threads=4.
문서 40개, 질문 34개인 합성 내부 평가입니다. 실자료나 독립 검수 결과가 아닙니다.

| Split | Method | Recall@5 | MRR@5 | nDCG@5 | p50 ms | p95 ms |
|---|---|---:|---:|---:|---:|---:|
| dev | bm25 | 1.0000 | 0.8958 | 0.9218 | 0.57 | 0.82 |
| dev | dense | 0.6250 | 0.5417 | 0.5233 | 17.80 | 18.90 |
| dev | rerank | 0.6250 | 0.6944 | 0.6116 | 286.25 | 298.67 |
| test | bm25 | 0.8889 | 0.8611 | 0.8684 | 0.62 | 0.84 |
| test | dense | 0.8333 | 0.6352 | 0.6482 | 18.70 | 19.59 |
| test | rerank | 0.8611 | 1.0000 | 0.8925 | 288.89 | 301.75 |

## 관찰과 한계

- test에서 BM25가 Recall@5 0.8889로 가장 높습니다. 키워드·연도·지역이 반복되는 합성 자료의 특성이 영향을 주었을 수 있습니다. 이는 원인 확정이 아니라 후속 실험 가설입니다.
- 리랭커는 test의 모든 정답 있는 질문에서 첫 번째 문서를 정답으로 배치했습니다(MRR@5=1). 다만 복수 정답 질문에서 일부 정답을 놓치므로 Recall@5는 1이 아닙니다.
- 리랭커의 test p50은 약 289ms로 BM25 약 0.62ms보다 큽니다. 이 작은 corpus의 단일 CPU 실행이며 운영 부하 시험이 아닙니다.
- dev에서는 리랭킹 후에도 Recall@5가 0.625입니다. 좋은 test 수치만 골라 제시하면 안 됩니다.
- 모든 방식이 정답 없는 질문에도 후보를 반환합니다. 보류 정책은 아직 미구현입니다.
- 이 결과를 확인한 이후 test에 맞춰 수정하면 새로운 독립 holdout이 필요합니다.

원본 질의별 결과, 모델 revision, 전체 패키지 버전은
[neural-comparison artifact](https://github.com/juyoo0729/retrieval-benchmark-lab/actions/runs/41170845618/artifacts/13030697139)에 있습니다.
artifact는 GitHub 보관 기간의 적용을 받습니다. 아래 summary.json은 실행 로그에서 추출한 집계이며 원시 질의 결과를 대체하지 않습니다.

원시 결과를 저장소에도 보관했습니다: [dev](../neural-dev/results.json), [test](../neural-test/results.json), [패키지 목록](../../requirements-resolved.txt). 위 artifact가 만료되어도 이 파일들은 남습니다.
