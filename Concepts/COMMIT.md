---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 1
unique_proposition_count: 1
concept_degree: 4
bridge_role: medium
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# COMMIT

## 한 줄 정의

[[Transaction]]의 변경 내용을 DB에 영구 반영하는 명령이다.

## 핵심 규칙

- COMMIT 이후에는 [[ROLLBACK]]으로 되돌릴 수 없다.
- COMMIT 이후에는 다른 사용자도 변경 결과를 조회할 수 있다.
- [[DDL]] 실행 시 Oracle에서는 자동으로 COMMIT이 발생한다([[AUTO COMMIT]]).

## 판단 순서

1. 어느 시점에 COMMIT이 발생했는지(명시적 COMMIT 또는 DDL로 인한 자동 COMMIT) 확인한다.
2. 그 이후의 ROLLBACK은 이 시점 이전으로 영향을 주지 못함을 적용한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| COMMIT vs ROLLBACK | COMMIT은 확정, ROLLBACK은 취소 |

## 대표 함정

- DDL로 인한 자동 COMMIT 시점을 놓치고 이후 ROLLBACK이 그 이전까지 되돌린다고 착각(M01-Q40).

## 연결된 문제

- [[M01-Q17]]

## 능동 회상 질문

1. COMMIT 이후 ROLLBACK으로 되돌릴 수 있는가?
2. Oracle에서 자동으로 COMMIT이 발생하는 경우는?

## 답 확인

1. 없다(되돌릴 수 없다).
2. DDL을 실행했을 때.

## 관련 개념

- COMMIT은 [[TCL]]에 속하는 명령어다.
- [[ROLLBACK]]은 COMMIT과 대조되는 트랜잭션 종료 명령이다.
- [[DDL]]은 Oracle에서 실행 시 자동으로 COMMIT을 유발한다([[AUTO COMMIT]]).

## Source

- SQL 관리 구문.md — 2. TCL(COMMIT)
