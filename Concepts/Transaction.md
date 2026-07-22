---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 3
unique_proposition_count: 4
concept_degree: 4
bridge_role: medium
direct_question_count: 2
supporting_question_count: 1
study_status: unverified
---

# Transaction

## 한 줄 정의

하나 이상의 SQL 문을 묶은 논리적 작업 단위이며, 전부 성공하거나 전부 취소된다.

## 핵심 규칙

- 명시적 트랜잭션: BEGIN TRANSACTION 후 [[COMMIT]]/[[ROLLBACK]]으로 직접 종료한다.
- 묵시적 트랜잭션: DML 실행 시 자동 시작되며 COMMIT/ROLLBACK 전까지 유지된다.
- [[ACID]](원자성/일관성/고립성/지속성) 속성을 지켜야 한다.
- Oracle의 [[DDL]] 실행은 자동으로 트랜잭션을 확정(COMMIT)시킨다.
- LOCK은 COMMIT 또는 ROLLBACK 시 해제된다.

## 판단 순서

1. 어떤 명령들이 하나의 트랜잭션으로 묶여 있는지 순서대로 나열한다.
2. DDL이 중간에 실행되었다면 그 시점에서 자동 COMMIT이 발생하는지(Oracle) 확인한다.
3. ROLLBACK이 등장하면 "마지막 COMMIT 시점"까지만 되돌아간다는 것을 적용한다.
4. 최종 상태를 각 단계별로 순서대로 추적한다.

## 자주 혼동하는 개념

| 비교 대상                     | 차이                                                       |
| ------------------------- | -------------------------------------------------------- |
| 명시적 vs 묵시적 트랜잭션           | 명시적은 BEGIN TRANSACTION으로 시작, 묵시적은 DML 실행 시 자동 시작         |
| ROLLBACK vs DROP/TRUNCATE | ROLLBACK은 DML 트랜잭션 취소, DROP/TRUNCATE는 DDL이라 애초에 되돌릴 수 없음 |

## 대표 함정

- 여러 DML과 DDL이 섞인 순서에서, DDL 이후의 ROLLBACK이 DDL 이전 상태까지 모두 되돌린다고 오판(M01-Q40).
- ACID의 각 속성 정의를 서로 바꿔서 착각(원자성=전부성공/실패, 지속성=영구보존, 일관성=규칙유지, 고립성=간섭방지)(M01-Q34).

## 연결된 문제

- [[M01-Q17]]
- [[M01-Q34]]
- [[M01-Q40]]

## 능동 회상 질문

1. 트랜잭션이 묵시적으로 시작되는 시점은 언제인가?
2. ROLLBACK은 어느 시점까지 되돌리는가?
3. Oracle에서 DDL 실행이 트랜잭션에 미치는 영향은?
4. ACID 중 "전부 성공 또는 전부 실패"에 해당하는 속성은?

## 답 확인

1. DML 실행 시 자동으로 시작된다.
2. 마지막 COMMIT 시점까지 되돌린다.
3. 자동으로 COMMIT을 발생시켜 그 이전 변경사항까지 확정한다.
4. 원자성(Atomicity).

## 관련 개념

- [[TCL]]은 Transaction을 제어하는 명령어 분류이며, Transaction 자체는 DML·DDL·DCL·TCL과 같은 명령어 분류가 아니다.
- Transaction은 [[COMMIT]]으로 확정되고 [[ROLLBACK]]으로 취소된다.
- [[ACID]]는 트랜잭션이 지켜야 할 4가지 속성을 정의한다.
- [[DDL]](Oracle)은 실행 시 트랜잭션을 자동으로 확정시킨다([[AUTO COMMIT]]).

## Source

- SQL 관리 구문.md — 2. TCL(트랜잭션)
