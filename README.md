# Retrieval Benchmark Lab · 한국어 검색 비교 실험실

같은 질문과 문서에서 **BM25 → 임베딩 검색 → 임베딩 + 리랭커**를 비교합니다.
검색기가 연도·지역·단위가 비슷한 문서를 혼동하는지, 의미가 같은 다른 표현을 찾는지 확인하는 학습 프로젝트입니다.

> **현재 데이터는 AI가 작성한 합성 메타데이터입니다. 실제 KOSIS 수치/공식 문서를 수집한 결과가 아닙니다.**
> 개발·테스트 질문은 주제별로 분리했지만 같은 작성 방식의 내부 예제입니다. 독립적인 일반화 성능으로 해석하지 마세요.
> 최초 로컬 검증: 자동 테스트 10개 통과, BM25 실행 완료. 신경망 비교는 GitHub Actions의 실행 결과를 확인해야 합니다.

## 왜 만들었나

RAG를 실행하는 것에서 한 단계 더 나아가, 검색 품질을 동일 조건에서 측정하는 연습입니다.
도구를 많이 붙이는 대신 정답셋, 지표 분모, 실패 기록, 재현 정보를 먼저 갖춥니다.

- 문서 40개, 질문 34개: dev 14개 / test 20개
- 정답이 있는 질문 30개 + 자료 범위 밖 질문 4개
- 정확한 표현, 바꿔 쓴 표현, 복수 정답·연도 비교
- 동일 질의·정답·문서에서 Recall@5, MRR@5, nDCG@5 비교
- 질의별 순위·점수·오류·지연, 데이터 SHA256, 모델 revision 기록
- 모델 초기화 실패를 성공한 비교처럼 숨기지 않음
- 실행 결과 덮어쓰기 금지

## 빠른 실행 · 추가 설치 없는 BM25

Python 3.11 이상, 저장소 루트에서 실행합니다.

```bash
python -m unittest discover -s tests -v
python -m retrieval_lab.cli --split dev --output results/local-dev-01
python -m retrieval_lab.cli --split test --output results/local-test-01
```

결과 폴더에 `report.md`와 `results.json`이 생깁니다.
같은 경로를 재사용하면 오류를 내므로 다음 실행에는 02 등 새 이름을 사용하세요.

## 세 방식 비교

처음 실행 시 공개 모델 가중치를 내려받습니다. 유료 API 키가 필요하지 않지만 다운로드와 CPU 계산 시간이 필요합니다.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[neural]"
python -m retrieval_lab.cli --methods bm25 dense rerank --split dev --output results/local-compare-dev
python -m retrieval_lab.cli --methods bm25 dense rerank --split test --output results/local-compare-test
```

GitHub Actions의 **Neural comparison** 워크플로도 같은 명령을 실행합니다.
결과는 실행 페이지의 artifact로 저장됩니다. CI 테스트 통과와 신경망 비교 실행 성공은 별개입니다.

기본 모델은 학습용 비교 기준이며 한국어 검색에 최적이라고 가정하지 않습니다.

| 방식 | 구현 |
|---|---|
| BM25 | 단어 + 한글 2글자 조각, k1=1.5 / b=0.75 |
| Dense | paraphrase-multilingual-MiniLM-L12-v2, 정규화 벡터의 내적 |
| Rerank | Dense 상위 10개를 mmarco-mMiniLMv2-L12-H384-v1로 재정렬 |

`--k 5 --candidates 10 --device cpu`가 기본입니다. 리랭커는 후보 밖 문서를 복구할 수 없습니다.
모델 버전을 재사용할 때 결과 JSON의 SHA를 `--embedding-revision`, `--reranker-revision`으로 전달하세요.

## 최초 BM25 결과 · 실제 실행

| 분할 | 정답 질문 | 정답 없음 | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|---:|---:|
| dev | 12 | 2 | 1.0000 | 0.8958 | 0.9218 |
| test | 18 | 2 | 0.8889 | 0.8611 | 0.8684 |

전체 원시 결과: [dev](results/baseline-dev/report.md), [test](results/baseline-test/report.md).
작고 템플릿화된 예제의 결과이며 성능 보증이 아닙니다.
자료가 없는 질문 4개에도 후보를 반환했습니다. **검색 결과가 있다는 것과 답할 근거가 있다는 것은 다릅니다.**

## 지표 해석

- Recall@k: 해당 질문의 전체 정답 문서 중 상위 k개에서 찾은 비율
- MRR@k: 상위 k개 중 첫 정답 순위의 역수. 찾지 못하면 0
- nDCG@k: 정답이 앞쪽에 있을수록 높은 점수. 현재 정답은 이진 관련도
- 정확도 지표의 분모는 해당 split의 **모든 정답 있는 질문**. 시스템 오류도 0으로 포함
- 정답 없는 질문은 별도 집계. 아직 보류 임계값을 보정하지 않아 HOLD 정확도를 주장하지 않음
- p50/p95는 성공한 검색 요청의 지연만 집계. 모델 로딩·문서 인덱싱은 별도 기록
- 리랭킹 시간에는 후보 검색이 포함. 요청별 배치 크기 1, 워밍업 1회, CPU 스레드 4개
- 단일 소규모 실행이므로 운영 처리량/부하 성능으로 해석하지 않음

## 구성

- `retrieval_lab/`: 입력 검증, 검색기, 지표, CLI
- `data/`: 합성 문서/질문, [데이터 카드](data/README.md)
- `tests/`: 손계산 지표, 오류 분모, 정답 없는 질문, 데이터 검증, CLI
- `docs/`: [실험 계획](docs/experiment-plan.md), [직접 학습할 순서](docs/learning-guide.md)
- `results/`: 실제 실행 기록
- `.github/workflows/`: 테스트와 신경망 비교

## 다음 실험

1. dev 오류를 보고 가설을 하나만 선택한다.
2. 동일 데이터에서 설정 하나만 바꿔 비교한다.
3. test는 설정 선택에 사용하지 않는다. 이미 결과를 보고 조정했다면 새로운 holdout을 만든다.
4. 실제 공공통계 자료를 출처·시점·사용 조건과 함께 수집한다.
5. 별도 사람이 질문·정답을 검수하고 내부 합성 결과와 분리해서 보고한다.

## 기여 범위

초기 코드·합성 예제·문서는 AI 코딩 도우미와 함께 작성했습니다.
이를 본인의 독자 구현이나 검수 완료 데이터라고 주장하지 않습니다.
직접 수행한 수정·실험·검토는 이후 커밋과 실험 기록에 남깁니다.

## 참고

- [Sentence Transformers 사용법](https://sbert.net/docs/quickstart.html)
- [검색 평가기](https://www.sbert.net/docs/package_reference/sentence_transformer/evaluation.html)
- [임베딩 모델 카드](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [리랭커 모델 카드](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1)
