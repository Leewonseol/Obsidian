# SQLD Learning DAG — 구현 전 데이터 검사 및 설계 계획

> 입력: `SQLD_knowledge_graph_v0_4.xlsx` (21개 시트)
> 이 문서는 구현 시작 전에 Excel을 파싱해 확인한 구조와 DAG 구축 방식을 요약한다.
> 구현 후 실제 빌드 수치는 `data/validation_report.json`과 README를 기준으로 한다.

## 1. 노드 수

| 구분 | 수 | 출처 |
|---|---:|---|
| 전체 노드 (`16_KG_Nodes`) | 527 | ROOT 1 + DOMAIN 7 + CLUSTER 41 + DIALECT 3 + Concept 475 |
| Concept (CONCEPT/SYNTAX/FUNCTION/RULE) | 475 | 264 / 97 / 66 / 48 |
| 현행 증거 Concept (`10_Current_Evidence`, 52회 이후) | 286 | Evidence Status = `CURRENT_EVIDENCE` |
| 구범위 전용 Concept (`11_Legacy_Only`) | 185 | `OLDER_EVIDENCE_ONLY` 139 + `LEGACY`(D7 등 범위 밖) 46 |
| 증거 없음 / 강의계획 참조 | 4 | `PIVOT·UNPIVOT`, `데이터 모델링 3단계`, `엔터티 분류`, `IN·NOT IN` |
| 마인드맵 gap Concept (`13_Current_Mindmap_Gaps`) | 191 | 새 노드 103 + 기존 노드 세분화 88 (모두 현행 증거 보유) |

검증 결과: 286 + 185 + 4 = 475. 10/11/13 시트의 Concept 이름은 모두 `16_KG_Nodes`에 존재하고,
gap 191개는 전부 현행 Concept이며 Legacy와 겹치지 않는다.

주의: Concept 이름은 Concept끼리는 유일하지만, CLUSTER 이름과 같은 Concept이 14개 있다
(`엔터티`, `JOIN`, `윈도우 함수`, `계층형 질의`, `DML`, `VIEW` 등). 모든 조인은 **Node ID** 기준으로 한다.

## 2. Edge type 분포 (`17_KG_Edges`, 625개)

| Relation | 수 | Learning DAG 처리 |
|---|---:|---|
| BELONGS_TO | 519 | 계층(hierarchy) 표시 전용. prerequisite 아님 |
| AFFECTS | 30 | metadata (영향/함정) |
| IS_A | 16 | metadata. 필요한 경우만 별도 근거로 inferred prerequisite 생성 |
| DIALECT_OF | 13 | metadata (DBMS 차이) |
| CONTRASTS | 11 | comparison card |
| USES | 8 | metadata |
| PRECEDES | 4 | **DAG 후보** (논리 실행순서 — 학습 선수관계인지 개별 검토) |
| REQUIRES | 3 | **DAG 후보** |
| ENABLES | 3 | **DAG 후보** |
| EXPLAINS | 3 | **DAG 후보** (실제 선수 의미가 있을 때만) |
| EXCEPTION | 3 | metadata (함정) |
| DIALECT | 2 | metadata |
| IMPLEMENTS | 2 | metadata |
| ENFORCES | 2 | metadata |
| REMOVED_BY | 2 | metadata |
| INCREASES_NEED_FOR / RESOLVED_BY / DIALECT_EQUIVALENT / ALTERNATIVE_TO | 1씩 | metadata |

→ 원본에 명시된 prerequisite 후보는 **13개뿐**이다. 475개 Concept의 학습 순서를 만들려면
선수관계 추론(inferred, 근거 기록)이 필수다.

### 명시 후보 13개 사전 검토

| Edge | 판단 |
|---|---|
| WHERE PRECEDES GROUP BY | 채택 (WHERE 행 필터를 알아야 GROUP BY 이전 단계를 이해) |
| GROUP BY PRECEDES HAVING / GROUP BY REQUIRES HAVING | 채택 (하나의 edge로 병합) |
| **HAVING PRECEDES SELECT** | **검토 대상** — *논리 실행순서*이지 학습 선수관계가 아님. 학습상 SELECT가 HAVING보다 먼저이므로 `SELECT → … → HAVING` 경로와 합쳐지면 cycle 발생 예상 |
| SELECT PRECEDES ORDER BY | 채택 |
| SELECT ENABLES ORDER BY 별칭 | 채택 |
| SQL 논리 실행 순서 EXPLAINS SELECT 별칭 WHERE 사용 불가 / ORDER BY 별칭 | 채택 |
| OUTER JOIN 조건 위치 EXPLAINS ON vs WHERE | 채택 |
| 함수적 종속 REQUIRES 2NF / 3NF | 채택 |
| NOCYCLE ENABLES CONNECT_BY_ISCYCLE | 채택 |
| SAVEPOINT ENABLES ROLLBACK TO SAVEPOINT | 채택 |

## 3. Stage별 Concept 수 (`16_KG_Nodes`의 Learning Stage 기준, 원본 그대로)

| Stage | 학습 블록 | Cluster | Concept | 현행 | 구범위 전용 | 참조 | gap |
|---|---|---|---:|---:|---:|---:|---:|
| 0 | 모델링 기초 | DM0–DM4 | 72 | 46 | 24 | 2 | 25 |
| 1 | 키·정규화·무결성 | DM5–DM7 | 45 | 22 | 23 | 0 | 12 |
| 2 | SQL 실행 모델 | SQ0–SQ5 | 77 | 55 | 21 | 1 | 37 |
| 3 | 표현식·함수 | FN1–FN5 | 53 | 32 | 21 | 0 | 18 |
| 4 | 관계 결합 | JN1, SQ6, SQ7 | 45 | 33 | 12 | 0 | 25 |
| 5 | 집계 | AG1, AG2 | 25 | 23 | 2 | 0 | 15 |
| 6 | 고급 조회 | AG3–AG5, HQ1 | 52 | 37 | 14 | 1 | 37 |
| 7 | 데이터·객체 관리 | MG1–MG4 | 42 | 20 | 22 | 0 | 11 |
| 8 | 트랜잭션·권한 | MG5, MG6 | 23 | 18 | 5 | 0 | 11 |
| 9 | DBMS 방언·시험 함정 | XC1, XC2 | **0** | 0 | 0 | 0 | 0 |
| Legacy | 성능·분산·PL/SQL·물리조인 | LG1–LG5 | 41 | 0 | 41 | 0 | 0 |

발견 사항:

1. **Stage 9에는 Concept가 하나도 없다.** XC1에는 DIALECT 노드 3개(ANSI/ISO SQL, Oracle SQL, SQL Server)만,
   XC2(실행순서·시험 함정)는 비어 있다. → `04_Mindmap_Gaps`의 gap family(“NULL 정렬 DBMS 차이”,
   “Top-N DBMS 방언”, “문자열 함수 DBMS 차이”, “별칭 가시성”, “OUTER JOIN 필터 위치”)를 근거로
   **통합(INTEGRATION) 노드**를 소수 추가해 Stage 9를 학습 경로의 종착점으로 만든다. `synthetic: true` 표시.
2. **Stage 배치가 학습 순서와 어긋난 Concept**가 있다. 예: `CHECK`, `UNIQUE`, `제약조건`, `DEFAULT`, `CTAS`가
   Stage 2(SELECT·FROM·별칭)에, `GROUP BY NULL`이 Stage 2(NULL)에, `문자형 MIN/MAX`가 Stage 3에,
   `개체 무결성`·`참조 무결성`이 Stage 0(DM0)에 있다. 이대로 두면 prerequisite가 뒤 Stage → 앞 Stage로
   역행한다. → **placement override**로 Cluster를 옮기되, 원래 위치와 이유를 노드에 기록한다.
3. 원본 마인드맵 상위 Concept 중 노드가 없는 라벨(`논리 연산자`, `날짜형 함수`, `ANSI JOIN`, `FROM` 등)이 있다.
   → 계층상 Cluster 바로 아래에 두고 원래 라벨을 `original_parent_label`로 보존한다.
4. 7개 Concept은 BELONGS_TO 부모가 2개다(예: `CURRENT ROW` → 윈도우 함수, ROWS/RANGE 프레임).
   → 더 구체적인 Concept 부모를 primary parent로 선택한다.

## 4. 현행 / Legacy 구분 방식

- 사용자 정의 Legacy = `11_Legacy_Only`의 185개 (52회 이후 현행 증거 없음). 삭제하지 않는다.
- 단, `SELECT`, `JOIN`, `OUTER JOIN`, `식별자`, `INSERT`, `WITH 절`, `CTE`처럼 **현행 Concept의 선수/상위 개념인
  구범위 전용 Concept**를 숨기면 학습 경로가 끊긴다(예: `LEFT OUTER JOIN`은 현행이지만 `OUTER JOIN`은 구범위 전용).
  → 이런 노드는 Priority **C(보조 · 구조적으로 필요)**로 기본 화면에 표시하되 “구범위 증거만 있음” 배지를 붙인다.
- 나머지 Legacy(현행 Concept 어느 것의 선수/상위도 아닌 것, D7 성능·옵티마이저·분산 DB·PL/SQL·물리 조인 전부)는
  기본 화면에서 숨기고 **Include Legacy** 토글로만 표시한다.

## 5. DAG 구축 방식

```
Stage (10 + Legacy)          ← 18_Learning_DAG backbone
  └ Cluster (41)             ← 19_Study_Outline_v2 / 16_KG_Nodes Cluster
      └ Concept (475 + 통합/구조 노드 소수)
          prerequisite ──▶ next concept   ← Learning DAG 본체
```

1. **Learning DAG (`networkx.DiGraph`)**
   - 노드: Concept 전체 + 합성 노드(통합·구조) + Stage/Cluster anchor
   - edge: ① 명시 prerequisite(REQUIRES/PRECEDES/ENABLES/EXPLAINS 중 검토 통과분)
     ② inferred prerequisite(`inferred: true`, `reason` 필수, 손으로 큐레이션한 목록에서만 생성)
     ③ Stage backbone(`18_Learning_DAG`의 선수 단계) ④ prerequisite가 없는 Concept → 소속 Cluster root anchor
   - semantic similarity, 공동 출제, degree/centrality로 edge를 만들지 않는다.
2. **Hierarchy (`hierarchy_edges.json`)**: Stage→Cluster→Concept→하위 Concept. 시각적으로 prerequisite와 구분.
3. **Metadata (`metadata_relations.json`)**: CONTRASTS, AFFECTS, DIALECT*, EXCEPTION, IS_A, IMPLEMENTS, USES 등은
   상세 패널의 “시험 비교 / 관련 개념 / 함정 / DBMS 차이”로만 사용.
4. **Full source graph (`networkx.MultiDiGraph`)**: 원본 625 edge 전체를 내부 검증용으로만 유지.
   CONTRASTS 같은 대칭 관계를 방향 간선으로 넣으면 cycle이 생긴다는 것을 진단 리포트에 함께 남긴다.
5. **Cycle 처리**: 후보 그래프에서 `nx.is_directed_acyclic_graph`가 false면 edge를 임의 삭제하지 않고
   `cycle_report.json`에 cycle과 의심 edge를 기록한 뒤, prerequisite 관계만 재검토하여 결정(채택/metadata 재분류)과
   이유를 남긴다. 최종 Learning DAG는 `is_dag: true`여야 한다.
6. **검증**: Stage 단조성(선수 Stage ≤ 다음 Stage), 현행 Concept 누락 0, gap Concept 누락 0,
   기본 화면 노드가 숨겨진 노드에 의존하지 않을 것, 모든 inferred edge에 reason 존재.

## 6. 우선순위 (중심성/degree 사용 안 함)

| Priority | 규칙 |
|---|---|
| A | 현행 2회 이상 출제 **그리고** (다른 현행 Concept의 직접 선수 **또는** 시험 함정 2개 이상 **또는** 비교 카드 대상), 또는 현행 4회 이상 |
| B | 현행 출제 확인(1회 이상), A 조건 미충족 |
| C | 현행 증거 없음/적음이지만 현행 Concept의 선수·상위 개념(구조적으로 필요), 또는 합성 구조 노드 |
| Legacy | 11_Legacy_Only 중 C에 해당하지 않는 것 — 기본 숨김 |

## 7. 산출물 계획

```
sqld-learning-dag/
  SQLD_knowledge_graph_v0_4.xlsx
  PLANNING.md / README.md
  scripts/build_learning_graph.py, scripts/validate_graph.py
  scripts/curation/   (inferred prerequisite · placement override · 합성 노드 · 규칙/함정 · 비교 카드 · 방언)
  data/   nodes, prerequisite_edges, hierarchy_edges, rules, comparisons, dialects, stages, legacy_nodes,
          metadata_relations, evidence, inferred_edges, validation_report, cycle_report
  web/    index.html, app.js, style.css, data.js(빌드 시 생성되는 번들 — file://에서도 동작)
```
