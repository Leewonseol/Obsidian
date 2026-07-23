---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 4
unique_proposition_count: 6
concept_degree: 7
bridge_role: high
direct_question_count: 3
supporting_question_count: 1
study_status: unverified
axis_membership:
  - modeling_to_join
  - sql_writing_order
  - oracle_sqlserver
axis_confidence: medium
axis_review_required: false
---

# DDL

## 한 줄 정의

테이블·뷰 등 객체와 구조를 정의·변경·삭제하는 명령어군(CREATE/ALTER/DROP/RENAME/TRUNCATE)이다.

## 핵심 규칙

- CREATE: 객체(TABLE, VIEW) 생성
- [[ALTER]]: 기존 객체 구조 변경(Oracle MODIFY / SQL Server ALTER COLUMN)
- [[DROP]]: 객체 자체(구조+데이터) 삭제
- [[TRUNCATE]]: 데이터만 삭제, 구조는 유지, WHERE 불가
- Oracle에서 DDL을 실행하면 자동으로 [[AUTO COMMIT]]이 발생해, 그 이전의 [[DML]] 변경 사항까지 함께 확정된다.

## 판단 순서

1. 명령어가 객체·구조를 정의/변경하는지(DDL), 데이터 값을 조회·삽입·수정·삭제하는지(DML), 권한을 부여·회수하는지(DCL), Transaction을 확정·취소·저장점 관리하는지(TCL) 먼저 분류한다.
2. DDL이라면 Oracle 환경인지 확인한다 — Oracle에서는 이 시점에 자동 COMMIT이 발생한다.
3. 그 DDL 이전에 커밋되지 않은 DML이 있었다면, 그 변경 내용이 이 시점에 함께 확정됨을 반영한다.
4. 이후 ROLLBACK은 이 확정 시점 이전으로 되돌릴 수 없다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| DDL vs DML | DDL은 구조(CREATE/ALTER/DROP/TRUNCATE), DML은 데이터(INSERT/UPDATE/DELETE) |
| DROP vs TRUNCATE | DROP은 구조까지 삭제, TRUNCATE는 구조 유지 |
| Oracle vs SQL Server AUTO COMMIT | Oracle은 DDL 실행 시에만 자동 커밋, SQL Server는 기본이 AUTO COMMIT |

## 대표 함정

- DDL(CREATE TABLE 등)이 실행되면 그 이전의 DML 변경 사항이 자동으로 커밋된다는 점을 놓치고, 이후 ROLLBACK이 모든 것을 되돌린다고 오판(M01-Q40).
- TRUNCATE를 DML(DELETE)처럼 ROLLBACK 가능하다고 착각(M01-Q46).

## 연결된 문제

- [[M01-Q17]]
- [[M01-Q40]]
- [[M01-Q46]]
- [[M01-Q47]]

## 능동 회상

### 1. Oracle에서 DDL을 실행하면 어떤 일이 자동으로 일어나는가?

> [!success]- 답 확인
> 자동으로 COMMIT이 발생한다.

### 2. DDL 실행 이전의 커밋되지 않은 DML은 이후 ROLLBACK으로 되돌릴 수 있는가?

> [!success]- 답 확인
> 되돌릴 수 없다(이미 DDL 시점에 확정되었으므로).

### 3. DROP과 TRUNCATE는 각각 테이블 구조를 어떻게 처리하는가?

> [!success]- 답 확인
> DROP은 구조까지 삭제, TRUNCATE는 구조를 유지한다.

### 4. DDL에 속하는 명령어 4가지는 무엇인가?

> [!success]- 답 확인
> CREATE, ALTER, DROP, TRUNCATE(및 RENAME).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- DDL 실행은 Oracle에서 [[AUTO COMMIT]]을 유발해 [[Transaction]]을 확정시킨다.
- [[ROLLBACK]]은 DDL로 확정된 시점 이전으로는 되돌릴 수 없다.
- [[DROP]], [[TRUNCATE]], [[ALTER]]는 모두 DDL의 하위 명령이다.

## Source

- SQL 관리 구문.md — 3. DDL
