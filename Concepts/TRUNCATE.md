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

# TRUNCATE

## 한 줄 정의

테이블의 모든 행을 삭제하되 테이블 구조는 유지하는 [[DDL]] 명령이다.

## 핵심 규칙

- WHERE절을 사용할 수 없다(전체 삭제만 가능).
- 실행 즉시 자동 COMMIT되어 일반적으로 ROLLBACK이 불가능하다.
- UNDO 로그를 남기지 않아 [[DELETE]]보다 빠르다.
- 테이블 구조는 그대로 유지된다.

## 판단 순서

1. DELETE가 아니라 TRUNCATE임을 먼저 확인한다(DDL이라는 뜻).
2. WHERE절 사용 여부를 확인한다 — 있으면 오답 함정.
3. ROLLBACK 가능 여부를 DDL 규칙으로 판단한다(불가능).

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| TRUNCATE vs DELETE | TRUNCATE는 WHERE 불가·ROLLBACK 불가, DELETE는 둘 다 가능 |
| TRUNCATE vs DROP | TRUNCATE는 구조 유지, DROP은 구조까지 삭제 |

## 대표 함정

- TRUNCATE를 ROLLBACK으로 복구 가능하다고 착각(M01-Q46).
- TRUNCATE에 WHERE를 붙일 수 있다고 착각(M01-Q47).

## 연결된 문제

- [[M01-Q46]]
- [[M01-Q47]]

## 능동 회상 질문

1. TRUNCATE는 WHERE절을 사용할 수 있는가?
2. TRUNCATE가 DELETE보다 빠른 이유는?

## 답 확인

1. 없다.
2. UNDO 로그를 남기지 않기 때문이다.

## 관련 개념

- [[DELETE]]·[[DROP]]과 삭제 명령 3종 세트를 이룬다.
- [[DDL]]이므로 실행 즉시 자동 COMMIT된다.

## Source

- SQL 관리 구문.md — 3. DDL(TRUNCATE, 삭제 명령 비교)
