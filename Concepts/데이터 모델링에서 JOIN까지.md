---
type: concept
concept_kind: structural_axis
axis_id: modeling_to_join
graph_role: structural_axis
include_in_learning_graph: true
exclude_from_concept_centrality: true
---

# 데이터 모델링에서 JOIN까지

## 1. 축의 정의

업무 요구사항 분석에서 출발해 개념적·논리적 데이터 모델링을 거쳐 정규화로 무결성을 확보하고, 물리적 구현(테이블·컬럼·PK·FK)으로 내려간 뒤, 필요하면 반정규화를 거쳐, 최종적으로 SQL 조회 단계에서 JOIN으로 관계를 복원하는 흐름 전체를 관통하는 축이다. 상하위 목차가 아니라 하나의 파이프라인이며, 다른 3개 축(SQL 작성 순서·SQL 논리적 실행 순서·Oracle과 SQL Server 차이)과 자유롭게 겹칠 수 있다.

**주의**: JOIN은 논리적 모델링 단계에서 실행되지 않는다. 논리적 모델링은 관계를 *설계*하고, 물리적 모델은 PK·FK로 *구현*하며, SQL 조회 시 JOIN은 관계를 *복원*한다. 반정규화는 정규화(무결성 우선)와 달리 조회 성능 향상·JOIN 감소가 목적이다.

## 2. 전체 학습 흐름

```
업무 요구사항
  → [[데이터 모델링 관점]]
  → 개념적·논리적 데이터 모델링
       [[엔터티]] · [[엔터티 분류]] · [[속성]] · [[식별자]] · [[관계]]
       [[관계 차수]] · [[관계 선택성]] · [[식별 관계]] · [[비식별 관계]] · [[ERD]]
  → [[함수적 종속]]과 이상 현상
  → [[정규화]]
  → 물리적 구현: [[PK]] · [[FK]] · [[제약조건]] · [[개체 무결성]] · [[참조 무결성]] · [[자료형]]
       (실행 수단: [[DDL]])
  → (필요 시 반정규화)
  → SQL 조회 단계에서 [[JOIN]]으로 관계 복원
```

[[NULL]]은 PK 존재성 규칙(주식별자는 NULL 불가)을 통해 이 파이프라인 전체에 걸쳐 있다.

## 3. 소속 Concept 목록 (23개)

[[데이터 모델링 3단계]] · [[데이터 모델링 관점]] · [[엔터티]] · [[엔터티 분류]] · [[속성]] · [[식별자]] · [[관계]] · [[관계 차수]] · [[관계 선택성]] · [[식별 관계]] · [[비식별 관계]] · [[ERD]] · [[함수적 종속]] · [[정규화]] · [[PK]] · [[FK]] · [[개체 무결성]] · [[참조 무결성]] · [[제약조건]] · [[자료형]] · [[DDL]] · [[JOIN]] · [[NULL]]

## 4. 핵심 Concept (그래프 betweenness 상위 5)

1. [[NULL]] — 4개 축 모두에 걸치는 유일한 Concept, 전체 betweenness 1위
2. [[PK]]
3. [[ERD]]
4. [[식별자]]
5. [[JOIN]] — 축 A의 마지막 단계, B·C축과도 겹침

## 5. 검토 필요 Concept

- [[JOIN]] — axis_review_required: true (Oracle 구식 OUTER JOIN(+) 차이가 본문에 없어 D축은 제외됨. A축 자체는 확정)
- [[자료형]] — axis_review_required: true (Oracle 자료형만 서술되어 있고 SQL Server와의 명시적 대조가 없어 D축 후보에서 보류됨. A축 자체는 medium confidence로 확정)

## 6. 관련 Question·Proposition 수 요약

이 축 소속 23개 Concept의 evidence_question_count 합계는 52, evidence_proposition_count 합계는 128이다(동일 문제/선지가 여러 Concept에 중복 집계될 수 있음).
