---
type: concept
pilot: true
origin:
  - current-map
  - mock-01
learning_tier: 1
unique_question_count: 2
unique_proposition_count: 8
concept_degree: 10
bridge_role: high
direct_question_count: 2
supporting_question_count: 0
study_status: unverified
axis_membership:
  - modeling_to_join
axis_confidence: high
axis_review_required: false
---

# ERD

## 한 줄 정의

엔터티·속성·관계를 도식화해 데이터가 어디에 있고 어떤 경로로 조인해야 하는지 보여주는 데이터베이스의 지도다.

## 핵심 규칙

- IE 표기법과 Barker 표기법이 있으며, NOT NULL 표현·카디널리티 표현·식별자 표기(#기호)·식별/비식별 관계 표기(bar 기호) 등에서 차이가 있다.
- Barker 표기법은 식별 관계일 때 관계선에 bar(|) 기호를 붙인다. bar가 없으면 비식별 관계다.
- IE 표기법은 엔터티 내부에서 식별자 속성과 일반 속성을 선으로 구분해 표현하지만, NULL 여부는 표현하지 못한다.
- [[관계 차수]]를 통해 JOIN 결과 행 수 변화를 예측하고, [[관계 선택성]]을 통해 OUTER JOIN 필요 여부를 판단한다.

## 판단 순서

1. 다이어그램이 IE 표기법인지 Barker 표기법인지 먼저 식별한다.
2. 관계선에 bar(|) 등 식별 관계 표시가 있는지 확인한다 — 있으면 식별 관계, 없으면 비식별 관계.
3. 관계 차수(1:1, 1:N, N:M)를 읽어 JOIN 시 행 수 변화를 예측한다.
4. 관계 선택성(필수/선택 참여)을 읽어 OUTER JOIN이 필요한지 판단한다.

## 자주 혼동하는 개념

| 비교 대상 | 차이 |
|---|---|
| IE 표기법 vs Barker 표기법 | IE는 NULL 여부 표현 불가, Barker는 *기호로 NOT NULL 표현 가능 |
| 식별 관계 vs 비식별 관계 | Barker에서 bar 기호 유무로 구분 |
| 관계 차수 vs 관계 선택성 | 차수는 "몇 개"(1:N), 선택성은 "필수인지 선택인지" |

## 대표 함정

- IE와 Barker 표기법이 NOT NULL 여부를 "둘 다" 표현할 수 있다고 오해(M01-Q09).
- 다이어그램에 bar 기호가 없는데도 식별 관계라고 판단(M01-Q10).

## 연결된 문제

- [[M01-Q09]]
- [[M01-Q10]]

## 능동 회상

### 1. Barker 표기법에서 식별 관계는 어떤 기호로 표현되는가?

> [!success]- 답 확인
> 관계선에 붙는 bar(|) 기호.

### 2. IE 표기법과 Barker 표기법 중 NOT NULL 여부를 표현할 수 있는 것은?

> [!success]- 답 확인
> Barker 표기법만 가능하다(IE는 불가능).

### 3. ERD의 관계 차수는 JOIN 결과에 어떤 영향을 예측하게 하는가?

> [!success]- 답 확인
> 1:N 관계에서 1쪽 행이 N쪽 수만큼 반복될 수 있음을 예측하게 한다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- ERD는 [[엔터티]], [[관계]], [[관계 차수]], [[관계 선택성]]을 시각적으로 표현하는 지도다.
- ERD상의 [[식별 관계]]·[[비식별 관계]]는 bar 기호로 구분된다.
- ERD는 [[PK]]·[[FK]]가 실제로 어떻게 연결되는지 보여준다.

## Source

- 데이터 모델링.md — 6. 데이터 모델링 3단계(개념적 데이터 모델링: "ERD 작성") — 표기 규칙 자체는 원본에 없어 PDF 해설로 보강됨
