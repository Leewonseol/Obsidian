---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 2
unique_proposition_count: 5
concept_degree: 5
bridge_role: medium
direct_question_count: 2
supporting_question_count: 0
study_status: unverified
---

# JOIN

## 한 줄 정의

여러 테이블의 데이터를 조인 조건으로 연결해 한 번에 조회하는 연산이다.

## 핵심 규칙

- 실행 원리: 테이블 간 모든 조합(카티션 곱)을 만든 뒤 조인 조건으로 필터링한다.
- 조인 조건은 일반적으로 [[PK]]–[[FK]] 열을 사용하며, 테이블 N개 조인 시 최소 N-1개 조건이 필요하다.
- [[관계 차수]]가 1:N이면 조인 결과에서 1쪽 행이 N쪽 수만큼 반복될 수 있다.
- 하위 유형: [[OUTER JOIN]](불일치 포함), INNER JOIN(불일치 제외), [[CROSS JOIN]](카티션 곱, 조건 없음).

## 판단 순서

1. 몇 개의 테이블이 조인되는지, 조인 조건이 몇 개 필요한지 확인한다.
2. 조인 조건이 없다면 CROSS JOIN(카티션 곱)인지 확인한다.
3. INNER인지 OUTER인지 구분해 불일치 행 처리 방식을 적용한다.
4. 결과 행 수를 관계 차수 또는 카티션 곱 공식으로 계산한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| INNER JOIN vs OUTER JOIN | INNER는 불일치 제외, OUTER는 불일치 포함(NULL 채움) |
| JOIN vs CROSS JOIN | JOIN은 조건 필요, CROSS JOIN은 조건 없이 모든 조합 |

## 대표 함정

- CROSS JOIN에 조인 조건이 없어야 정상인데 "조건이 없어 오류"라고 착각(M01-Q39).
- LEFT OUTER JOIN 결과에서 매칭되지 않은 행이 어떻게 되는지 잘못 판단(M01-Q27).

## 연결된 문제

- [[M01-Q27]]
- [[M01-Q39]]

## 능동 회상

### 1. 두 테이블을 조인할 때 결과 행의 기본 원리는 무엇인가(조건 적용 전)?

> [!success]- 답 확인
> 모든 가능한 조합(카티션 곱)을 만든 뒤 조건으로 필터링한다.

### 2. CROSS JOIN에 조인 조건(ON)을 쓸 수 있는가?

> [!success]- 답 확인
> 쓸 수 없다(CROSS JOIN은 조건이 없어야 한다).

### 3. 1:N 관계에서 JOIN 결과 행 수는 어떻게 변하는가?

> [!success]- 답 확인
> 1쪽 행이 N쪽 수만큼 반복되어 늘어난다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[JOIN]]은 [[PK]]–[[FK]] 관계를 조건으로 사용하는 경우가 많다.
- [[관계 차수]]는 JOIN 결과의 행 수 변화를 예측하게 한다.
- [[OUTER JOIN]]과 [[CROSS JOIN]]은 각각 다른 방식으로 JOIN의 기본 원리(카티션 곱+필터링)를 응용한 형태다.

## Source

- SQL 기본.md — 5. FROM 절(JOIN)
