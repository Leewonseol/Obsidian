---
type: concept
concept_kind: structural_axis
axis_id: sql_execution_order
graph_role: structural_axis
include_in_learning_graph: true
exclude_from_concept_centrality: true
---

# SQL 논리적 실행 순서

## 1. 축의 정의

DBMS가 쿼리를 논리적으로 처리하여 중간 행 집합을 만드는 순서를 다루는 축이다. [[SQL 작성 순서]](사용자가 타이핑하는 순서)와는 별개이며 혼동하지 않는다.

## 2. 전체 학습 흐름

```
FROM
  → [[JOIN]] / ON  ([[CROSS JOIN]] · [[OUTER JOIN]])
  → [[WHERE]]
  → [[GROUP BY]] ([[그룹함수 확장]])
  → [[HAVING]]
  → SELECT
  → DISTINCT
  → [[윈도우 함수]]
  → [[ORDER BY]]
  → 행 제한
```

각 단계의 결과를 입력으로 받는 요소:
- [[서브쿼리]] — SELECT/FROM/WHERE/HAVING 등 여러 단계에서 결과가 입력으로 소비된다.
- [[집합 연산자]] — 두 개 이상의 완결된 SELECT 파이프라인 결과를 입력으로 받는다.
- [[집계 함수]]([[COUNT]] 포함) — GROUP BY 단계 이후 각 그룹을 입력으로 받는다.
- [[윈도우 함수]] — SELECT 처리 이후, ORDER BY 이전 단계에서 파티션 내 행을 입력으로 받는다.
- [[NULL]] — WHERE 필터링·GROUP BY/집계 제외·JOIN 채움·ORDER BY 정렬 등 파이프라인 전 단계에서 서로 다른 처리 규칙이 적용된다.

## 3. 소속 Concept 목록 (14개)

[[COUNT]] · [[CROSS JOIN]] · [[GROUP BY]] · [[HAVING]] · [[JOIN]] · [[NULL]] · [[ORDER BY]] · [[OUTER JOIN]] · [[WHERE]] · [[그룹함수 확장]] · [[서브쿼리]] · [[윈도우 함수]] · [[집계 함수]] · [[집합 연산자]]

## 4. 핵심 Concept (그래프 betweenness 상위 5)

1. [[NULL]]
2. [[ORDER BY]]
3. [[JOIN]]
4. [[집계 함수]]
5. [[WHERE]]

## 5. 검토 필요 Concept

- [[JOIN]] — A축 포함 여부와 별개로, D축(Oracle 구식 OUTER JOIN(+))은 본문 근거 부족으로 미포함
- [[OUTER JOIN]] — 동일 사유로 D축 미포함
- [[윈도우 함수]] — SQL Server 전용 서술(TOP WITH TIES)만 있어 D축 미포함
- [[집합 연산자]] — MINUS만 서술되고 EXCEPT/SQL Server 대조가 없어 D축 미포함

## 6. 관련 Question·Proposition 수 요약

이 축 소속 14개 Concept의 evidence_question_count 합계는 53, evidence_proposition_count 합계는 159다(중복 집계 가능).
