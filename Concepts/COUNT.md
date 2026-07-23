---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 3
unique_proposition_count: 9
concept_degree: 3
bridge_role: medium
direct_question_count: 3
supporting_question_count: 0
study_status: unverified
axis_membership:
  - sql_writing_order
  - sql_execution_order
axis_confidence: high
axis_review_required: false
---

# COUNT

## 한 줄 정의

행의 개수를 세는 [[집계 함수]]이며, 대상 표기 방식에 따라 [[NULL]] 처리 방식이 달라진다.

## 핵심 규칙

- COUNT(*): 모든 행을 계산하며 NULL도 포함한다.
- COUNT(열): 해당 열이 NULL인 행은 제외하고 계산한다.
- COUNT(1), COUNT(0): 상수는 NULL이 아니므로 COUNT(*)와 같은 결과를 낸다.
- COUNT(DISTINCT 열): 중복을 제거한 뒤 집계한다.

## 판단 순서

1. COUNT(*)인지 COUNT(열)인지 먼저 구분한다.
2. 대상 열에 NULL이 있는지 확인한다.
3. COUNT(*)라면 NULL 포함, COUNT(열)이라면 NULL 제외로 계산한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| COUNT(*) vs COUNT(열) | NULL 포함 여부 |

## 대표 함정

- OUTER JOIN으로 생긴 NULL이 있는 상황에서 COUNT(*)와 COUNT(열)을 혼동(M01-Q19).
- SUM/COUNT(*)를 조합한 평균 계산에서 COUNT(*)와 COUNT(열)의 값 차이를 놓침(M01-Q49).

## 연결된 문제

- [[M01-Q19]]
- [[M01-Q29]]
- [[M01-Q49]]

## 능동 회상

### 1. COUNT(*)와 COUNT(열)의 NULL 처리 차이는?

> [!success]- 답 확인
> COUNT(*)는 NULL 포함, COUNT(열)은 NULL 제외.

### 2. LEFT OUTER JOIN 결과에서 COUNT(열)은 무엇을 제외하는가?

> [!success]- 답 확인
> 매칭되지 않아 NULL이 된 행.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[집계 함수]] 중 유일하게 대상 표기(*, 열)에 따라 [[NULL]] 처리가 갈린다.
- [[OUTER JOIN]] 결과의 NULL과 자주 결합되어 출제된다.

## Source

- SQL 기본.md — 7. GROUP BY(② GROUP BY와 함께 쓰이는 집계 함수)
