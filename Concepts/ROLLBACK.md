---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 3
unique_proposition_count: 6
concept_degree: 4
bridge_role: medium
direct_question_count: 3
supporting_question_count: 0
study_status: unverified
axis_membership:
  - sql_writing_order
axis_confidence: high
axis_review_required: true
---

# ROLLBACK

## 한 줄 정의

[[Transaction]]에서 변경된 내용을 마지막 COMMIT 시점으로 되돌리는 명령이다.

## 핵심 규칙

- 마지막 [[COMMIT]] 이후의 변경 내용만 취소한다(그 이전은 되돌릴 수 없다).
- SAVEPOINT까지만 부분적으로 되돌릴 수도 있다.
- [[DDL]] 실행(Oracle 자동 COMMIT) 이후에는 그 이전 DML까지 함께 확정되어 되돌릴 수 없다.
- [[TRUNCATE]]·[[DROP]]은 DDL이라 일반적으로 ROLLBACK이 불가능하다.

## 판단 순서

1. 트랜잭션 내에서 COMMIT(명시적 또는 DDL로 인한 자동)이 발생한 시점을 찾는다.
2. ROLLBACK이 그 시점 "이후"의 변경만 취소함을 적용한다.
3. TRUNCATE/DROP처럼 애초에 ROLLBACK 대상이 아닌 명령인지 확인한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| ROLLBACK 대상 DML vs DDL | DML은 ROLLBACK 가능, DDL(TRUNCATE/DROP)은 불가능 |

## 대표 함정

- DDL 이후의 ROLLBACK이 DDL 이전 상태까지 모두 되돌린다고 오판(M01-Q40).
- TRUNCATE를 DELETE처럼 ROLLBACK 가능하다고 착각(M01-Q46).

## 연결된 문제

- [[M01-Q40]]
- [[M01-Q46]]
- [[M01-Q47]]

## 능동 회상

### 1. ROLLBACK은 어느 시점까지 되돌리는가?

> [!success]- 답 확인
> 마지막 COMMIT 시점까지.

### 2. TRUNCATE는 ROLLBACK으로 복구 가능한가?

> [!success]- 답 확인
> 불가능하다(DDL이므로 자동 COMMIT됨).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- ROLLBACK은 [[TCL]]에 속하는 명령어다.
- [[COMMIT]]과 대조되는 트랜잭션 취소 명령이다.
- [[DDL]] 실행(자동 COMMIT) 이후에는 ROLLBACK 범위가 제한된다.
- [[DELETE]]는 ROLLBACK 가능하지만 [[TRUNCATE]]·[[DROP]]은 불가능하다.

## Source

- SQL 관리 구문.md — 2. TCL(ROLLBACK)
