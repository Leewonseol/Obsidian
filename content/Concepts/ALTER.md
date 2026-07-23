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

# ALTER

## 한 줄 정의

기존 테이블 등 객체의 구조를 변경하는 [[DDL]] 명령이다.

## 핵심 규칙

- 컬럼 추가: ALTER TABLE 테이블 ADD ...
- 컬럼 삭제: ALTER TABLE 테이블 DROP ...
- 자료형·속성 변경: Oracle은 MODIFY, SQL Server는 ALTER COLUMN을 사용한다.
- Oracle MODIFY는 여러 컬럼을 괄호로 묶어 한 번에 변경할 수 있지만, SQL Server ALTER COLUMN은 한 번에 한 컬럼만 변경할 수 있다.

## 판단 순서

1. 자료형 표기(VARCHAR2=Oracle, VARCHAR=SQL Server)로 DBMS를 식별한다.
2. MODIFY(Oracle)인지 ALTER COLUMN(SQL Server)인지 확인한다.
3. 괄호로 여러 컬럼을 묶었다면 어느 DBMS에서 가능한지 판단한다(Oracle만 가능).

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| Oracle MODIFY vs SQL Server ALTER COLUMN | MODIFY는 다중 컬럼 동시 변경 가능, ALTER COLUMN은 한 번에 한 컬럼만 |

## 대표 함정

- SQL Server ALTER COLUMN으로 여러 컬럼을 괄호로 묶어 변경할 수 있다고 착각(M01-Q48).

## 연결된 문제

- [[M01-Q48]]

## 능동 회상

### 1. Oracle과 SQL Server에서 컬럼 자료형 변경 명령어는 각각 무엇인가?

> [!success]- 답 확인
> Oracle은 MODIFY, SQL Server는 ALTER COLUMN.

### 2. 여러 컬럼을 한 번에 변경할 수 있는 DBMS는?

> [!success]- 답 확인
> Oracle(MODIFY로 괄호 묶음 가능).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[DDL]]의 하위 명령 중 하나로, 기존 객체 구조를 변경한다.

## Source

- SQL 관리 구문.md — 3. DDL(ALTER)
