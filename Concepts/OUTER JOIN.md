---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 2
unique_proposition_count: 8
concept_degree: 3
bridge_role: medium
direct_question_count: 2
supporting_question_count: 0
study_status: unverified
---

# OUTER JOIN

## 한 줄 정의

조인 조건에 일치하지 않는 행도 포함하며, 매칭되지 않는 반대편 열은 NULL로 채우는 [[JOIN]] 방식이다.

## 핵심 규칙

- LEFT OUTER JOIN: 왼쪽 테이블 전체를 유지한다.
- RIGHT OUTER JOIN: 오른쪽 테이블 전체를 유지한다.
- FULL OUTER JOIN: 양쪽 전체를 유지한다(LEFT와 RIGHT 결과의 합집합).
- 불일치로 채워진 [[NULL]] 값은 이후 [[COUNT]](열) 등 집계 결과에 영향을 준다.

## 판단 순서

1. 기준 테이블이 왼쪽인지 오른쪽인지 확인한다.
2. 불일치 행이 어느 쪽에 NULL로 채워지는지 계산한다.
3. 이후 집계 함수가 있다면 NULL 처리 규칙을 이어서 적용한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| LEFT vs RIGHT OUTER JOIN | 기준이 되는(전체 유지되는) 테이블이 다름 |
| INNER JOIN vs OUTER JOIN | INNER는 불일치 제외, OUTER는 NULL로 채워 포함 |

## 대표 함정

- LEFT OUTER JOIN의 기준 테이블을 반대로 착각(M01-Q27).
- OUTER JOIN 결과의 NULL을 COUNT(*)와 COUNT(열)에 다르게 적용하지 못함(M01-Q19).

## 연결된 문제

- [[M01-Q19]]
- [[M01-Q27]]

## 능동 회상 질문

1. LEFT OUTER JOIN에서 전체가 유지되는 쪽은?
2. 불일치하는 행의 반대편 열은 어떤 값이 되는가?

## 답 확인

1. 왼쪽 테이블.
2. NULL.

## 관련 개념

- [[JOIN]]의 하위 유형이며, 불일치 시 [[NULL]]을 생성한다.
- 생성된 NULL은 [[COUNT]] 등 집계 함수 계산에 영향을 준다.

## Source

- SQL 기본.md — 5. FROM 절(JOIN, OUTER JOIN)
