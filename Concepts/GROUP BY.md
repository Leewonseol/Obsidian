---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 3
unique_proposition_count: 8
concept_degree: 4
bridge_role: medium
direct_question_count: 1
supporting_question_count: 2
study_status: unverified
axis_membership:
  - sql_writing_order
  - sql_execution_order
axis_confidence: high
axis_review_required: false
---

# GROUP BY

## 한 줄 정의

특정 열을 기준으로 같은 값끼리 묶어 데이터의 관찰 단위(입도)를 그룹 단위로 바꾸는 절이다.

## 핵심 규칙

- [[WHERE]] 이후, SELECT 이전에 실행된다.
- SELECT에서는 GROUP BY에 명시한 열·표현식과 [[집계 함수]]만 사용할 수 있다.
- [[HAVING]]으로 그룹을 추가 필터링할 수 있다.
- [[그룹함수 확장]](ROLLUP/CUBE/GROUPING SETS)으로 여러 집계 수준을 한 번에 낼 수 있다.
- SELECT 별칭은 논리적으로 SELECT 단계에서 만들어지고, [[SQL 논리적 실행 순서]]상 GROUP BY는 SELECT보다 먼저 처리된다. 따라서 같은 SELECT 목록에서 만든 별칭을 GROUP BY 절에서 바로 참조할 수 없다는 것이 표준적인 설명이다(Oracle 기준).
- 다만 일부 DBMS는 편의 기능으로 GROUP BY에서 SELECT 별칭 참조를 허용할 수 있으므로, 문제가 전제하는 DBMS를 먼저 확인해야 한다.
- 별칭 참조가 불확실한 경우, 다음처럼 GROUP BY 절에 원래 식을 그대로 반복하면 안전하다.

```sql
SELECT
    SUBSTR(code, 1, 1) AS code_group,
    COUNT(*)
FROM sample
GROUP BY SUBSTR(code, 1, 1);
```

## 판단 순서

1. 어떤 열을 기준으로 그룹화되는지 확인한다.
2. 그룹별로 집계 함수 결과를 계산한다.
3. HAVING 조건이 있으면 그룹 단위로 필터링한다.
4. SELECT 목록에 그룹화 열·집계 함수 외의 일반 열이 있는지 점검한다(있으면 오류).

## 자주 혼동하는 개념

| 비교 대상              | 차이                                      |
| ------------------ | --------------------------------------- |
| GROUP BY vs HAVING | GROUP BY는 그룹을 만들고, HAVING은 만들어진 그룹을 필터링 |
| GROUP BY vs WHERE  | WHERE는 그룹화 이전 행 필터, GROUP BY는 그 이후 그룹화  |

## 대표 함정

- WHERE절에 집계 조건을 넣어 오류가 나는 원인을 GROUP BY 구문 자체의 문제로 착각(M01-Q20).
- GROUP BY와 HAVING을 함께 쓸 때 HAVING 조건을 만족하지 못하는 그룹도 결과에 포함된다고 착각(M01-Q30).

## 연결된 문제

- [[M01-Q20]]
- [[M01-Q30]]
- [[M01-Q31]]

## 능동 회상

### 1. GROUP BY는 논리적 실행 순서상 WHERE보다 먼저인가, 나중인가?

> [!success]- 답 확인
> WHERE보다 나중이다.

### 2. GROUP BY 사용 시 SELECT에 올 수 있는 항목은 무엇인가?

> [!success]- 답 확인
> GROUP BY에 명시한 열·표현식과 집계 함수만 올 수 있다.

### 3. HAVING 조건을 만족하지 못한 그룹은 최종 결과에 포함되는가?

> [!success]- 답 확인
> 포함되지 않는다(HAVING이 걸러낸다).

### 4. SELECT에서 만든 열 별칭을 GROUP BY 절에서 바로 참조할 수 있는가?

> [!success]- 답 확인
> 표준적으로는 불가능하다(Oracle 기준). GROUP BY가 SELECT보다 먼저 처리되기 때문이며, 일부 DBMS만 편의 기능으로 허용할 수 있다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[GROUP BY]]는 [[집계 함수]]와 짝을 이루어 그룹별 계산을 수행한다.
- [[HAVING]]은 GROUP BY가 만든 그룹을 대상으로 추가 필터링을 한다.
- [[그룹함수 확장]](ROLLUP 등)은 GROUP BY를 확장해 여러 집계 수준을 동시에 산출한다.

## Source

- SQL 기본.md — 7. GROUP BY
- SELECT 별칭 참조 제한(Oracle): 유선배 기출변형 모의고사 1회(Q24) 해설 근거
