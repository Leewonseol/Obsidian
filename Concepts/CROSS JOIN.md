---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 3
unique_question_count: 1
unique_proposition_count: 4
concept_degree: 1
bridge_role: low
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# CROSS JOIN

## 한 줄 정의

조인 조건 없이 두 테이블의 모든 행 조합(카티션 곱)을 만드는 [[JOIN]] 방식이다.

## 핵심 규칙

- 결과 행 수 = 첫 번째 테이블 행 수 × 두 번째 테이블 행 수.
- ANSI 표준 CROSS JOIN 구문에는 ON을 사용할 수 없다(조인 조건 자체가 없어야 함).
- 구문형(FROM A, B에서 조건 생략)으로도 동일한 카티션 곱을 만들 수 있다.

## Related Concepts

- [[JOIN]]

## Source

- SQL 기본.md — 5. FROM 절(CARTESIAN JOIN, CROSS JOIN)
