---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 1
unique_proposition_count: 4
concept_degree: 1
bridge_role: low
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# ACID

## 한 줄 정의

[[Transaction]]이 지켜야 할 4가지 속성(원자성·일관성·고립성·지속성)이다.

## 핵심 규칙

- Atomicity(원자성): 전부 성공 또는 전부 실패(All or Nothing).
- Consistency(일관성): 실행 전후 DB의 규칙·제약조건 유지.
- Isolation(고립성): 동시 트랜잭션 간 간섭 방지.
- Durability(지속성): COMMIT 결과는 영구 보존.

## 판단 순서

1. 문제 설명이 4가지 속성 중 어느 정의와 일치하는지 키워드로 매칭한다("전부/부분" → 원자성, "영구보존" → 지속성, "규칙유지" → 일관성, "간섭방지" → 고립성).

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| 원자성 vs 지속성 | 원자성은 성공/실패 여부, 지속성은 확정 후 보존 여부 |

## 대표 함정

- "전부 성공 또는 전부 실패"를 지속성·일관성·고립성 중 하나로 잘못 연결(M01-Q34).

## 연결된 문제

- [[M01-Q34]]

## 능동 회상 질문

1. "전부 성공 또는 전부 실패"는 어떤 속성인가?
2. COMMIT 결과가 영구 보존되는 것은 어떤 속성인가?

## 답 확인

1. 원자성(Atomicity).
2. 지속성(Durability).

## 관련 개념

- [[Transaction]]이 지켜야 하는 이론적 근거를 제공한다.

## Source

- SQL 관리 구문.md — 2. TCL(ACID)
