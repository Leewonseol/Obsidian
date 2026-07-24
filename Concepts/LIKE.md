---
type: concept
pilot: true
origin:
  - yuseonbae-mock-01
learning_tier: 3
unique_question_count: 0
unique_proposition_count: 0
concept_degree: 0
bridge_role: low
direct_question_count: 0
supporting_question_count: 0
study_status: unverified
axis_membership:
  - sql_writing_order
axis_confidence: medium
axis_review_required: true
---

# LIKE

## 한 줄 정의

문자열이 지정한 패턴과 일치하는지 판정하는 조건 연산자이며, 주로 WHERE·HAVING의 조건식에서 사용된다.

## 핵심 규칙

- 기본 문법: `expression LIKE pattern`, `expression NOT LIKE pattern`
- `%`: 길이가 0 이상인 임의 문자열과 일치(0글자도 포함)
- `_`: 임의의 문자 정확히 1개와 일치
- `'A%'`는 A로 시작, `'%A'`는 A로 끝남, `'%A%'`는 A를 포함, `'A_'`는 A 다음에 정확히 한 글자가 오는 값과 일치
- ESCAPE로 `%`·`_` 자체를 리터럴 문자로 검색할 수 있다: `LIKE '%\%%' ESCAPE '\'`는 문자 그대로의 `%`를 포함하는 값을 찾는다는 뜻이다
- `NULL LIKE pattern`은 TRUE·FALSE가 아니라 UNKNOWN이며, WHERE에서는 해당 행이 통과하지 않는다
- `NOT LIKE`도 마찬가지로 NULL 행은 통과시키지 않는다(NULL 행까지 포함하려면 `OR column IS NULL`을 별도로 추가해야 한다)

## 판단 순서

1. 패턴에 `%`와 `_`가 각각 몇 개, 어느 위치에 있는지 먼저 확인한다.
2. ESCAPE 문자가 지정되어 있는지 확인하고, 있다면 그 다음에 오는 와일드카드 기호를 리터럴로 해석한다.
3. 비교 대상 값이 NULL인지 확인한다(NULL이면 결과는 항상 UNKNOWN이다).
4. NOT LIKE인 경우에도 NULL 행 처리가 LIKE와 동일하다는 점을 마지막에 확인한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| `%` vs `_` | `%`는 0글자 이상, `_`는 정확히 1글자 |
| LIKE vs NOT LIKE + NULL | 둘 다 NULL 행은 통과시키지 않는다(NOT LIKE가 NULL까지 포함한다고 착각하기 쉽다) |
| ESCAPE 유무 | ESCAPE 없이 `%`·`_` 자체를 검색하려 하면 와일드카드로 해석되어 의도와 다르게 매칭된다 |

## SQLD 함정

- `%`를 "한 글자 이상"으로 잘못 이해(실제로는 0글자 이상)
- `_`를 "0글자 이상"으로 잘못 이해(실제로는 정확히 1글자)
- ESCAPE 없이 `%`·`_` 자체를 검색하려는 오류
- `NOT LIKE`가 NULL 행까지 포함한다고 착각하는 오류
- 대소문자 구분 여부는 DBMS·collation에 따라 달라지므로 문제에서 명시한 조건을 우선한다(과도한 일반화 금지)

## 능동 회상

### 1. `%`와 `_`는 각각 몇 글자와 일치하는가?

> [!success]- 답 확인
> `%`는 0글자 이상, `_`는 정확히 1글자와 일치한다.

### 2. `NULL LIKE '%A%'`의 결과는 TRUE인가 FALSE인가?

> [!success]- 답 확인
> 둘 다 아니다. UNKNOWN이며, WHERE에서는 해당 행이 통과하지 않는다.

### 3. 패턴에 포함된 `%` 자체를 리터럴 문자로 검색하려면 무엇이 필요한가?

> [!success]- 답 확인
> ESCAPE로 이스케이프 문자를 지정하고, 그 문자를 `%` 앞에 붙인다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## Related Concepts

- [[NULL]]과 결합 시 LIKE 비교 결과가 TRUE·FALSE가 아니라 UNKNOWN이 될 수 있다.
- [[WHERE]] 조건식에서 다른 조건과 함께 사용된다.
- [[문자형 함수]]와는 성격이 다르다(문자열 값을 가공하지 않고 패턴 일치만 판정하는 조건 연산자다).

## Source

- 원본에 없음(유선배 기출변형 모의고사 1회 Q38 해설 근거) — 보강 필요
