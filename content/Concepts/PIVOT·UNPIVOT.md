---
type: concept
pilot: true
origin:
  - mock-01
learning_tier: 3
unique_question_count: 1
unique_proposition_count: 4
concept_degree: 1
bridge_role: low
direct_question_count: 1
supporting_question_count: 0
study_status: unverified
---

# PIVOT·UNPIVOT

## 한 줄 정의

행과 열을 서로 전환해 데이터를 재구성하는 SQL 연산이다(PIVOT: 행→열, UNPIVOT: 열→행).

## 핵심 규칙

- 원본 마인드맵에는 PIVOT·UNPIVOT 자체에 대한 서술이 전혀 없다.
- PDF 해설 기준: UNPIVOT에서 EXCLUDE NULLS 옵션을 사용하면 측정치가 [[NULL]]인 행이 결과에서 제외된다.

## 능동 회상

### 1. PIVOT과 UNPIVOT은 각각 어떤 방향으로 데이터를 재구성하는가?

> [!success]- 답 확인
> PIVOT은 행→열, UNPIVOT은 열→행으로 재구성한다.

### 2. UNPIVOT에서 EXCLUDE NULLS 옵션을 사용하면 어떤 행이 제외되는가?

> [!success]- 답 확인
> 측정치가 NULL인 행이 결과에서 제외된다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## Related Concepts

- [[NULL]]

## Source

- 원본에 없음(mock-01 해설 근거) — 보강 필요
