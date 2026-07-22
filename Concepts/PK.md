---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 2
unique_proposition_count: 4
concept_degree: 7
bridge_role: high
direct_question_count: 1
supporting_question_count: 1
study_status: unverified
---

# PK

## 한 줄 정의

테이블에서 각 행을 유일하게 식별하는 기본키 제약조건이다.

## 핵심 규칙

- 중복된 값을 허용하지 않는다(유일성).
- [[NULL]]을 허용하지 않는다(존재성).
- 한 테이블에 하나만 지정할 수 있다(복합키로 여러 컬럼을 묶을 수 있음).
- 데이터 모델링의 [[식별자]] 개념이 SQL 구현 단계에서 PK로 대응된다.

## 판단 순서

1. 문제에서 다루는 제약이 "유일성"인지 "NULL 허용 여부"인지 구분한다.
2. PK와 다른 제약조건(UNIQUE, NOT NULL)을 혼동하지 않았는지 확인한다.
3. [[개체 무결성]]과 연결되는 문제인지(PK 위반=개체 무결성 위반) 판단한다.

## 자주 혼동하는 개념

| 비교 대상        | 차이                                     |
| ------------ | -------------------------------------- |
| PK vs UNIQUE | 둘 다 중복 방지, PK는 NULL 불가·UNIQUE는 NULL 허용 |
| PK vs FK     | PK는 NULL 불가, FK는 NULL 가능               |

## 대표 함정

- UNIQUE 제약조건 설정을 PK 위반(개체 무결성 위반)과 혼동(M01-Q01).
- FK가 참조하는 대상이 PK뿐 아니라 UNIQUE 키일 수도 있다는 점을 놓침(M01-Q07).

## 연결된 문제

- [[M01-Q01]]
- [[M01-Q07]]

## 능동 회상 질문

1. PK와 UNIQUE의 공통점과 차이점은?
2. PK 컬럼에 NULL을 저장하면 어떤 무결성 위반인가?
3. FK는 반드시 PK만 참조할 수 있는가?

## 답 확인

1. 둘 다 중복을 허용하지 않지만, PK는 NULL을 허용하지 않고 UNIQUE는 허용한다.
2. 개체 무결성 위반이다.
3. PK뿐 아니라 UNIQUE 키도 참조할 수 있다.

## 관련 개념

- PK는 [[NULL]]을 허용하지 않는다는 것이 [[개체 무결성]]의 핵심 규칙이다.
- PK는 데이터 모델링의 [[식별자]] 개념이 SQL로 구현된 형태다.
- [[FK]]는 다른 테이블의 PK(또는 UNIQUE)를 참조한다.

## Source

- 데이터 모델링.md — 9. 식별자(주식별자 특징: 유일성/최소성/불변성/존재성)
- SQL 관리 구문.md — 3. DDL 제약조건(PRIMARY KEY: 중복 X, NULL X, 테이블당 하나(복합키 가능))
