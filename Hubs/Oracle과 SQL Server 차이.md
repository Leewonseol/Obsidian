---
type: hub
axis_id: oracle_sqlserver
exclude_from_centrality: true
---

# Oracle과 SQL Server 차이

## 1. 축의 정의

SQLD 범위에서 **명시적으로 다른 것만** 이 축으로 분류한다. 차이가 명시되지 않은 부분은 공통 SQL 개념으로 간주하며, 다른 Concept 전체에 이 차이를 과잉 적용하지 않는다. 이번 2차 단계에서는 본문에 Oracle·SQL Server 양쪽이 실제로 대조 서술된 5개 Concept만 확정 상태로 유지한다.

## 2. 전체 학습 흐름

이 축은 파이프라인이 아니라 개별 대조 항목의 모음이다.

- 자료형 변경 문법: Oracle `MODIFY` vs SQL Server `ALTER COLUMN` → [[ALTER]]
- 커밋 시점: Oracle(DML 수동/DDL 자동) vs SQL Server(기본 자동) → [[AUTO COMMIT]] · [[DDL]]
- 정렬 시 NULL 위치 → [[NULL]] · [[ORDER BY]]

## 3. 소속 Concept 목록 (5개, 확정)

[[ALTER]] · [[AUTO COMMIT]] · [[DDL]] · [[NULL]] · [[ORDER BY]]

## 4. 핵심 Concept (그래프 betweenness 상위, 5개 전부)

1. [[NULL]] — 4개 축 모두에 걸치는 유일한 Concept
2. [[ORDER BY]]
3. [[DDL]]
4. [[ALTER]]
5. [[AUTO COMMIT]]

## 5. 검토 필요 Concept

이 축에는 review_required 항목이 없다(확정된 5개는 모두 axis_review_required: false). 대신 아래 14개는 **한쪽 DBMS만 언급되어 이번 단계에서 D축에 포함하지 않았고**, `_reports/검토필요-분류.md`에 후보로만 남아 있다. Oracle과 SQL Server 양쪽의 차이가 소스에서 확인되기 전까지는 포함하지 않는다.

COMMIT, DCL, DROP, ROLLBACK, Transaction, 계층형 질의, 문자형 함수, 윈도우 함수, 자료형, 정규표현식 함수, 집합 연산자, JOIN, OUTER JOIN, PIVOT·UNPIVOT

지시문이 예시로 든 항목 중 아래는 현재 어떤 Concept Node에도 대응하지 않는다(콘텐츠 공백, 신규 노드 생성 안 함): 문자열 연결(`||`/`+`), CHR/CHAR, SYSDATE/GETDATE, EXTRACT/DATEPART, NVL/ISNULL, DECODE.

## 6. 관련 Question·Proposition 수 요약

이 축 소속 5개 Concept의 evidence_question_count 합계는 25, evidence_proposition_count 합계는 67이다(중복 집계 가능).
