---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 3
unique_question_count: 1
unique_proposition_count: 2
concept_degree: 2
bridge_role: low
direct_question_count: 0
supporting_question_count: 1
study_status: unverified
---

# DML

## 한 줄 정의

테이블의 행 데이터를 삽입·수정·삭제하는 명령어군(INSERT/UPDATE/DELETE/MERGE)이다.

## 핵심 규칙

- INSERT: 행 삽입
- UPDATE: 기존 행의 값 수정
- [[DELETE]]: 조건에 맞는 행 삭제, ROLLBACK 가능
- MERGE: 대상 테이블과 소스 테이블을 병합(MATCHED/NOT MATCHED 처리)

## 능동 회상

### 1. DML에 속하는 4가지 명령어는 무엇인가?

> [!success]- 답 확인
> INSERT, UPDATE, DELETE, MERGE.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## Related Concepts

- [[DELETE]]

## Source

- SQL 관리 구문.md — 1. DML
