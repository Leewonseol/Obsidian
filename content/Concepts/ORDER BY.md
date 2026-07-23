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

# ORDER BY

## 한 줄 정의

조회 결과를 지정한 기준으로 정렬하는 절이며, 논리적 실행 순서상 가장 마지막에 실행된다.

## 핵심 규칙

- ASC(기본값)/DESC로 정렬 방향을 지정하며, 다중 열 정렬 시 각 열마다 별도로 지정 가능하다.
- 열 이름, SELECT 순서 번호, 별칭, CASE 표현식을 정렬 기준으로 사용할 수 있다.
- 문자형 [[자료형]] 정렬 시 숫자처럼 보여도 사전식 비교가 적용된다.
- NULL 정렬 순서는 Oracle과 SQL Server가 다르다.

## 판단 순서

1. 정렬 기준이 열 이름/별칭/순서번호 중 무엇인지 확인한다.
2. 각 기준 열마다 ASC/DESC가 개별 지정되어 있는지 확인한다(DESC는 바로 앞 열에만 적용).
3. 자료형이 문자형이면 사전식 비교를 적용한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| ORDER BY 1,2 DESC vs ORDER BY 1 DESC,2 | DESC 위치에 따라 적용 열이 달라짐 |
| 문자형 정렬 vs 숫자형 정렬 | 문자형은 사전식('99'>'100'), 숫자형은 크기순 |

## 대표 함정

- 문자형 컬럼을 숫자 크기로 착각해 정렬 순서를 잘못 예측(M01-Q15).
- ORDER BY 1,2 DESC에서 DESC가 모든 열에 적용된다고 착각(M01-Q36).

## 연결된 문제

- [[M01-Q15]]
- [[M01-Q24]]
- [[M01-Q36]]

## 능동 회상

### 1. ORDER BY 1,2 DESC에서 DESC는 몇 번째 열에 적용되는가?

> [!success]- 답 확인
> 2번째 열에만 적용된다.

### 2. 문자형 컬럼 '99'와 '100' 중 사전식으로 더 큰 값은?

> [!success]- 답 확인
> '99'가 더 크다('9'>'1'이므로).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[자료형]]이 문자형이면 ORDER BY도 사전식 비교를 따른다.
- [[NULL]]의 정렬 위치는 DBMS에 따라 다르다.

## Source

- SQL 기본.md — 8. ORDER BY
