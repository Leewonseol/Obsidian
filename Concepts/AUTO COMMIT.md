---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 1
unique_proposition_count: 4
concept_degree: 3
bridge_role: medium
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# AUTO COMMIT

## 한 줄 정의

SQL문 실행 직후 자동으로 [[COMMIT]]이 이루어지는지를 결정하는 설정이다.

## 핵심 규칙

- Oracle: 기본적으로 DML은 자동 COMMIT되지 않지만, [[DDL]] 실행 시에는 자동 COMMIT이 발생한다.
- SQL Server: 기본적으로 AUTO COMMIT 상태이며, BEGIN TRANSACTION을 명시하면 수동 제어로 전환할 수 있다.
- 이 DBMS별 차이는 Oracle 조건에서만 성립하며, SQL Server는 애초에 기본이 AUTO COMMIT이므로 "DDL이 원인"이라는 인과관계가 적용되지 않는다.

## 판단 순서

1. 문제의 DBMS가 Oracle인지 SQL Server인지 확인한다.
2. Oracle이면 DDL 실행 시점에서 자동 COMMIT이 발생함을 적용한다.
3. SQL Server라면 기본값 자체가 AUTO COMMIT임을 적용한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| Oracle vs SQL Server | Oracle은 DDL 시에만 자동 커밋, SQL Server는 기본이 자동 커밋 |

## 대표 함정

- Oracle의 "DDL 자동 커밋" 규칙을 놓쳐 여러 단계 트랜잭션 흐름에서 최종 상태를 잘못 계산(M01-Q40).

## 연결된 문제

- [[M01-Q40]]

## 능동 회상 질문

1. Oracle에서 DML은 기본적으로 자동 커밋되는가?
2. SQL Server의 기본 커밋 방식은?

## 답 확인

1. 되지 않는다(DDL 실행 시에만 자동 커밋).
2. 기본적으로 AUTO COMMIT 상태다.

## 관련 개념

- [[DDL]]은 Oracle에서 AUTO COMMIT을 유발해 [[Transaction]]을 확정시킨다.

## Source

- SQL 관리 구문.md — 2. TCL(AUTO COMMIT)
