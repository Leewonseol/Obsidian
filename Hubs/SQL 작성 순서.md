---
type: hub
axis_id: sql_writing_order
exclude_from_centrality: true
---

# SQL 작성 순서

## 1. 축의 정의

사용자가 SQL 문장을 작성할 때의 표면 문법 순서와, 각 절·구문이 들어갈 수 있는 위치를 다루는 축이다. [[SQL 논리적 실행 순서]](DBMS가 처리하는 순서)와는 별개이며 혼동하지 않는다.

## 2. 전체 학습 흐름

```
SELECT → FROM → [[JOIN]]([[CROSS JOIN]] · [[OUTER JOIN]]) → ON
  → [[WHERE]]([[IN·NOT IN]])
  → [[GROUP BY]]([[그룹함수 확장]])
  → [[HAVING]]
  → [[ORDER BY]]
```

그 외 문법 요소:
- 집합 연산자: [[집합 연산자]]
- 서브쿼리: [[서브쿼리]]
- 함수: [[집계 함수]]([[COUNT]]) · [[윈도우 함수]] · [[문자형 함수]] · [[숫자형 함수]] · [[정규표현식 함수]]
- 계층형 질의: [[계층형 질의]]
- 행/열 재구성: [[PIVOT·UNPIVOT]]
- DML·DDL·DCL·TCL 문법: [[DML]]([[DELETE]]) · [[DDL]]([[ALTER]] · [[DROP]] · [[TRUNCATE]] · [[제약조건]] · [[VIEW]]) · [[DCL]] · [[TCL]]([[COMMIT]] · [[ROLLBACK]] · [[AUTO COMMIT]] · [[Transaction]])
- 비교·연산 작성 규칙: [[NULL]]

## 3. 소속 Concept 목록 (34개)

[[ALTER]] · [[AUTO COMMIT]] · [[COMMIT]] · [[COUNT]] · [[CROSS JOIN]] · [[DCL]] · [[DDL]] · [[DELETE]] · [[DML]] · [[DROP]] · [[GROUP BY]] · [[HAVING]] · [[IN·NOT IN]] · [[JOIN]] · [[NULL]] · [[ORDER BY]] · [[OUTER JOIN]] · [[PIVOT·UNPIVOT]] · [[ROLLBACK]] · [[TCL]] · [[TRUNCATE]] · [[Transaction]] · [[VIEW]] · [[WHERE]] · [[계층형 질의]] · [[그룹함수 확장]] · [[문자형 함수]] · [[서브쿼리]] · [[숫자형 함수]] · [[윈도우 함수]] · [[정규표현식 함수]] · [[제약조건]] · [[집계 함수]] · [[집합 연산자]]

## 4. 핵심 Concept (그래프 betweenness 상위 5)

1. [[NULL]] — 4개 축 모두에 걸치는 유일한 Concept
2. [[ORDER BY]] — B·C·D 3축
3. [[JOIN]] — A·B·C 3축
4. [[집계 함수]]
5. [[WHERE]]

## 5. 검토 필요 Concept (14개 — Oracle/SQL Server 언급이 있으나 한쪽 DBMS만 서술되어 D축 미포함)

[[COMMIT]] · [[DCL]] · [[DROP]] · [[IN·NOT IN]] · [[JOIN]] · [[OUTER JOIN]] · [[PIVOT·UNPIVOT]] · [[ROLLBACK]] · [[Transaction]] · [[계층형 질의]] · [[문자형 함수]] · [[윈도우 함수]] · [[정규표현식 함수]] · [[집합 연산자]]

상세 근거는 `_reports/검토필요-분류.md` 참조. 본문 보강 없이 일반 지식으로 DBMS 차이를 추론해 넣지 않았다.

## 6. 관련 Question·Proposition 수 요약

이 축 소속 34개 Concept의 evidence_question_count 합계는 88, evidence_proposition_count 합계는 243이다(중복 집계 가능).
