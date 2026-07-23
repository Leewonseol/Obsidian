---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 3
unique_proposition_count: 9
concept_degree: 4
bridge_role: medium
direct_question_count: 2
supporting_question_count: 1
study_status: unverified
axis_membership:
  - sql_writing_order
  - sql_execution_order
axis_confidence: high
axis_review_required: false
---

# WHERE

## 한 줄 정의

행 단위로 조건을 걸어 필터링하는 절이며, [[GROUP BY]]보다 먼저 실행된다.

## 핵심 규칙

- 조건이 TRUE인 행만 통과하고, FALSE·UNKNOWN인 행은 제외된다.
- [[집계 함수]]는 WHERE절에서 사용할 수 없다(아직 그룹화·집계가 일어나지 않은 단계이므로).
- NULL 비교에는 IS NULL/IS NOT NULL만 사용할 수 있다.
- 논리적 실행 순서상 FROM/JOIN 다음, GROUP BY 이전에 실행된다.

## 판단 순서

1. 조건식에 집계 함수가 포함되어 있는지 먼저 확인한다 — 있으면 WHERE에서 오류가 난다.
2. NULL 비교가 있다면 IS NULL 사용 여부를 확인한다.
3. 여러 조건이 있으면 연산자 우선순위(괄호>비교>NOT>AND>OR)로 해석한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| WHERE vs HAVING | WHERE는 개별 행, 집계 함수 조건 불가 / HAVING은 그룹, 집계 함수 조건 가능 |
| WHERE COL=NULL vs WHERE COL IS NULL | 전자는 항상 UNKNOWN(오류 없이 0행), 후자만 정상 동작 |

## 대표 함정

- WHERE절에 SUM(SAL)>1000 같은 집계 조건을 그대로 써서 발생하는 오류의 원인을 GROUP BY나 SUM 문법 탓으로 잘못 판단(M01-Q20).
- WHERE COL=NULL이 문법 오류 없이 실행되지만 항상 빈 결과를 낸다는 것을 놓침(M01-Q32).

## 연결된 문제

- [[M01-Q13]]
- [[M01-Q20]]
- [[M01-Q31]]

## 능동 회상

### 1. WHERE와 HAVING 중 어느 것이 먼저 실행되는가?

> [!success]- 답 확인
> WHERE가 먼저 실행된다(GROUP BY 이전).

### 2. WHERE절에서 집계 함수를 조건으로 쓸 수 없는 이유는?

> [!success]- 답 확인
> WHERE 실행 시점에는 아직 그룹화·집계가 이루어지지 않았기 때문이다.

### 3. WHERE COL = NULL은 문법 오류인가, 아니면 항상 빈 결과를 내는가?

> [!success]- 답 확인
> 문법 오류는 아니지만 NULL은 =로 비교할 수 없어 항상 UNKNOWN이 되어 빈 결과를 낸다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[WHERE]]는 개별 행을, [[HAVING]]은 그룹을 필터링한다는 점에서 대조된다.
- [[집계 함수]]는 WHERE절에서 사용할 수 없고 HAVING절에서만 조건으로 쓸 수 있다.
- [[NULL]] 비교는 WHERE절에서 IS NULL로만 가능하다.

## Source

- SQL 기본.md — 6. WHERE 절
