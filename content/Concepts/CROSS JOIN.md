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

## 능동 회상

### 1. CROSS JOIN의 결과 행 수는 어떻게 계산하는가?

> [!success]- 답 확인
> 첫 번째 테이블 행 수 × 두 번째 테이블 행 수(카티션 곱).

### 2. ANSI 표준 CROSS JOIN 구문에 ON 조건절을 사용할 수 있는가?

> [!success]- 답 확인
> 사용할 수 없다(조인 조건 자체가 없어야 한다).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## Related Concepts

- [[JOIN]]

## Source

- SQL 기본.md — 5. FROM 절(CARTESIAN JOIN, CROSS JOIN)
