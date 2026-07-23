---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 2
unique_proposition_count: 4
concept_degree: 3
bridge_role: medium
direct_question_count: 2
supporting_question_count: 0
study_status: unverified
---

# DROP

## 한 줄 정의

테이블 객체 자체(구조+데이터)를 삭제하는 [[DDL]] 명령이다.

## 핵심 규칙

- 실행 후 테이블 자체가 존재하지 않게 된다.
- 일반적으로 ROLLBACK이 불가능하다.
- Oracle의 DROP TABLE에서는 CASCADE CONSTRAINTS 옵션을 사용하여 해당 테이블을 참조하는 제약조건을 함께 제거할 수 있다.
- [[DELETE]]·[[TRUNCATE]]와 달리 테이블 구조까지 완전히 없앤다는 점이 가장 큰 차이다.

## 판단 순서

1. DELETE/TRUNCATE/DROP 중 어느 것인지 구분한다.
2. 구조까지 삭제되는지(DROP만 해당) 확인한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| DROP vs TRUNCATE | DROP은 구조까지 삭제, TRUNCATE는 구조 유지 |

## 대표 함정

- DROP·TRUNCATE·DELETE 세 명령의 DML/DDL 분류와 구조 삭제 여부를 서로 바꿔 서술(M01-Q47).

## 연결된 문제

- [[M01-Q47]]

## 능동 회상

### 1. DROP 실행 후 테이블은 어떻게 되는가?

> [!success]- 답 확인
> 테이블 자체(구조+데이터)가 완전히 사라진다.

### 2. DROP은 DML인가 DDL인가?

> [!success]- 답 확인
> DDL.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[DELETE]]·[[TRUNCATE]]와 삭제 명령 3종 세트를 이룬다.

## Source

- SQL 관리 구문.md — 3. DDL(DROP, 삭제 명령 비교)
