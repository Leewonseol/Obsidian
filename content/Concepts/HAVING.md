---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 3
unique_proposition_count: 9
concept_degree: 3
bridge_role: medium
direct_question_count: 3
supporting_question_count: 0
study_status: unverified
---

# HAVING

## 한 줄 정의

[[GROUP BY]]로 만들어진 그룹을 필터링하는 절이며, GROUP BY 이후·SELECT 이전에 실행된다.

## 핵심 규칙

- [[집계 함수]] 결과를 조건으로 사용할 수 있다는 점에서 [[WHERE]]와 다르다.
- GROUP BY에 명시한 열이나 표현식은 사용할 수 있지만, 그룹화되지 않은 일반 열은 사용할 수 없다.

## 판단 순서

1. 그룹별 집계값을 먼저 계산한다.
2. HAVING 조건을 그 집계값에 적용해 그룹을 필터링한다.

## 자주 혼동하는 개념

| 비교 대상           | 차이                                               |
| --------------- | ------------------------------------------------ |
| HAVING vs WHERE | HAVING은 그룹 대상+집계함수 조건 가능, WHERE는 행 대상+집계함수 조건 불가 |

## 대표 함정

- HAVING 조건을 만족 못하는 그룹도 결과에 남는다고 착각(M01-Q30).

## 연결된 문제

- [[M01-Q20]]
- [[M01-Q30]]
- [[M01-Q31]]

## 능동 회상

### 1. HAVING은 WHERE와 달리 무엇을 조건으로 쓸 수 있는가?

> [!success]- 답 확인
> 집계 함수 결과.

### 2. HAVING은 GROUP BY 전에 실행되는가, 후에 실행되는가?

> [!success]- 답 확인
> 후에 실행된다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[WHERE]]와 대조되는 그룹 필터링 절이다.
- [[GROUP BY]]가 만든 그룹을 대상으로 작동한다.

## Source

- SQL 기본.md — 7. GROUP BY(③ HAVING 절)
