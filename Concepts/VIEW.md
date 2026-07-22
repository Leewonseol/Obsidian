---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 2
unique_question_count: 1
unique_proposition_count: 4
concept_degree: 1
bridge_role: low
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# VIEW

## 한 줄 정의

SELECT 문을 저장해 가상 테이블처럼 사용하는 객체다.

## 핵심 규칙

- 실제 행 데이터를 직접 저장하지 않고, 실행할 때 저장된 SELECT를 다시 수행한다.
- 단순 뷰는 DML이 가능하지만, 복합 뷰는 DML이 제한된다.
- 뷰 자체에는 인덱스를 생성할 수 없다.
- 여러 테이블을 조합(JOIN)한 SELECT도 뷰로 정의할 수 있다.

## 판단 순서

1. 단순 뷰인지 복합 뷰인지 확인한다.
2. DML 가능 여부를 묻는 문제라면 "항상 가능"이 아니라 "단순 뷰만 가능"임을 적용한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| 단순 뷰 vs 복합 뷰 | 단순 뷰는 DML 가능, 복합 뷰는 DML 제한 |

## 대표 함정

- 뷰를 통한 DML이 "항상" 가능하다고 절대화(M01-Q12).

## 연결된 문제

- [[M01-Q12]]

## 능동 회상 질문

1. 뷰는 데이터를 직접 저장하는가?
2. 복합 뷰에서 DML이 항상 가능한가?

## 답 확인

1. 저장하지 않는다(SELECT를 다시 실행).
2. 아니다(제한된다).

## 관련 개념

- VIEW는 저장된 SELECT문을 실행 시점에 재수행하는 객체다.

## Source

- SQL 관리 구문.md — VIEW
