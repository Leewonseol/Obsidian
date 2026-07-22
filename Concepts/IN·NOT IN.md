---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 3
unique_question_count: 1
unique_proposition_count: 1
concept_degree: 2
bridge_role: low
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# IN·NOT IN

## 한 줄 정의

여러 값 중 하나와 일치하는지(IN) 또는 일치하지 않는지(NOT IN)를 비교하는 연산자다.

## 핵심 규칙

- IN은 여러 OR 조건의 축약이다.
- NOT IN 목록에 [[NULL]]이 하나라도 포함되면 전체 비교 결과가 UNKNOWN이 되어 결과 자체가 나오지 않을 수 있다(3값 논리 관련, 원본에 "3값 논리"라는 용어 자체는 없음).

## Related Concepts

- [[NULL]]
- [[WHERE]]

## Source

- SQL 기본.md — 6. WHERE 절(IN)
