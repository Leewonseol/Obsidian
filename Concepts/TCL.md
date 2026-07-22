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

# TCL

## 한 줄 정의

[[Transaction]]을 제어하는 명령어 분류이며, COMMIT·ROLLBACK·SAVEPOINT가 대표 명령어다.

## 핵심 규칙

- TCL은 SQL 명령어 분류(DML/DDL/DCL/TCL) 중 하나이며, Transaction 자체는 명령어 분류가 아니라 TCL이 제어하는 대상 개념이다.
- [[COMMIT]]: 변경 내용을 영구 확정한다.
- [[ROLLBACK]]: 변경 내용을 마지막 COMMIT 시점으로 되돌린다.
- SAVEPOINT: 트랜잭션 중간에 저장점을 지정해 부분 롤백을 가능하게 한다.

## 판단 순서

1. 명령어가 트랜잭션(변경 확정/취소)을 제어하는지 확인한다 — 그렇다면 TCL이다.
2. TCL을 DCL(권한)이나 DDL(구조)과 혼동하지 않았는지 확인한다.
3. "Transaction"이라는 단어 자체를 명령어 분류로 잘못 나열하지 않았는지 점검한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| TCL vs DCL | TCL은 트랜잭션(COMMIT/ROLLBACK) 제어, DCL은 권한(GRANT/REVOKE) 제어 |
| TCL vs Transaction | TCL은 명령어 분류(무엇을 실행하는가), Transaction은 그 명령어가 제어하는 대상 개념(작업 단위) — 같은 층위가 아니다 |

## 대표 함정

- COMMIT을 DCL로 착각하거나, Transaction을 DML·DDL·DCL·TCL과 같은 층위의 명령어 분류로 잘못 나열(M01-Q17).

## 연결된 문제

- [[M01-Q17]]

## 능동 회상 질문

1. TCL의 대표 명령어 3가지는?
2. TCL과 Transaction은 같은 층위의 개념인가?

## 답 확인

1. COMMIT, ROLLBACK, SAVEPOINT.
2. 아니다. TCL은 명령어 분류이고 Transaction은 그 제어 대상이다.

## 관련 개념

- [[TCL]]은 [[Transaction]]을 제어하는 명령어 분류다.
- [[COMMIT]]과 [[ROLLBACK]]은 TCL에 속하는 명령어다.
- [[DCL]]·[[DDL]]·[[DML]]과 함께 SQL 명령어의 주요 분류를 이룬다.

## Source

- SQL 관리 구문.md — 2. TCL(Transaction Control Language)
