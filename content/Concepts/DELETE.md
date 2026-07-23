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
---

# DELETE

## 한 줄 정의

WHERE 조건에 맞는 행을 삭제하는 [[DML]] 명령이다.

## 핵심 규칙

- WHERE절로 삭제할 행을 선택할 수 있으며, 생략하면 모든 행이 삭제된다.
- 테이블 구조는 유지된다.
- DML이므로 [[ROLLBACK]]으로 복구할 수 있다.
- [[TRUNCATE]]·[[DROP]]과 함께 삭제 명령 3종 세트를 이룬다.

## 판단 순서

1. DELETE/TRUNCATE/DROP 중 무엇인지 구분한다.
2. WHERE 사용 가능 여부, 구조 유지 여부, ROLLBACK 가능 여부를 각각 대조한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| DELETE vs TRUNCATE | DELETE는 WHERE 가능·ROLLBACK 가능, TRUNCATE는 WHERE 불가·ROLLBACK 불가 |
| DELETE vs DROP | DELETE는 데이터만 삭제, DROP은 구조까지 삭제 |

## 대표 함정

- DELETE WHERE와 TRUNCATE WHERE가 동일한 결과를 낸다고 착각(TRUNCATE는 WHERE 자체가 불가능)(M01-Q47).

## 연결된 문제

- [[M01-Q46]]
- [[M01-Q47]]

## 능동 회상

### 1. DELETE는 ROLLBACK으로 복구할 수 있는가?

> [!success]- 답 확인
> 있다(DML이므로).

### 2. TRUNCATE에 WHERE절을 쓸 수 있는가?

> [!success]- 답 확인
> 없다(전체 삭제만 가능).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[TRUNCATE]]·[[DROP]]과 삭제 명령 3종 세트를 이룬다.
- DML이므로 [[ROLLBACK]] 가능하다는 점에서 DDL 계열과 다르다.

## Source

- SQL 관리 구문.md — 1. DML(DELETE), 3. DDL(삭제 명령 비교)
