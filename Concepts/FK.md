---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 2
unique_proposition_count: 5
concept_degree: 6
bridge_role: high
direct_question_count: 1
supporting_question_count: 1
study_status: unverified
axis_membership:
  - modeling_to_join
axis_confidence: high
axis_review_required: false
---

# FK

## 한 줄 정의

다른 테이블의 기본키를 참조하여 두 테이블 간 관계를 표현하는 외래키 제약조건이다.

## 핵심 규칙

- 참조 무결성을 보장한다 — 부모 테이블에 존재하는 값만 참조할 수 있다.
- 별도의 NOT NULL 제약이 없는 한 NULL 값을 가질 수 있다(PK와의 차이).
- 참조 테이블의 PK나 UNIQUE 키를 참조할 수 있다.
- CASCADE, SET NULL, SET DEFAULT, NO ACTION·RESTRICT 옵션을 가질 수 있다.

## 판단 순서

1. FK가 참조하려는 대상 값이 부모 테이블에 실제로 존재하는지 확인한다.
2. NULL 허용 여부는 별도 NOT NULL 제약이 없는 한 허용됨을 기본으로 판단한다.
3. FK 관련 옵션(CASCADE 등)이 문제에 언급되어 있으면 그 동작을 함께 고려한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| PK vs FK | PK는 NULL 불가·유일해야 함, FK는 NULL 가능·중복 가능 |
| FK vs 개체 무결성 | FK는 참조 무결성 대상, 개체 무결성은 PK 대상(서로 다른 무결성 범주) |

## 대표 함정

- 부모 테이블에 없는 값도 FK가 참조할 수 있다고 오해(참조 무결성 위반)(M01-Q07).
- FK가 부모 값을 정상적으로 참조하는 것을 "개체 무결성 위반"으로 착각(M01-Q01).

## 연결된 문제

- [[M01-Q01]]
- [[M01-Q07]]

## 능동 회상

### 1. FK는 부모 테이블에 없는 값을 참조할 수 있는가?

> [!success]- 답 확인
> 참조할 수 없다(참조 무결성 위반).

### 2. FK 컬럼은 NULL을 가질 수 있는가?

> [!success]- 답 확인
> 별도 NOT NULL 제약이 없는 한 가질 수 있다.

### 3. FK가 부모 값을 참조하는 것은 어떤 무결성과 관련되는가?

> [!success]- 답 확인
> 참조 무결성(개체 무결성이 아니다).

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- FK는 [[참조 무결성]]을 보장하며, [[개체 무결성]](PK 대상)과는 범주가 다르다.
- FK는 [[JOIN]] 조건으로 [[PK]]와 함께 가장 흔히 사용된다.
- FK는 데이터 모델링의 [[관계]]가 SQL로 구현된 형태다.

## Source

- SQL 관리 구문.md — 3. DDL 제약조건(FOREIGN KEY: 참조 무결성 보장)
