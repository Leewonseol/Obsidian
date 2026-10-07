# SQLD Learning DAG

`SQLD_knowledge_graph_v0_4.xlsx`를 기반으로 만든 **SQLD 시험 대비 학습 순서도(Learning DAG)** 웹앱입니다.

목표는 SQLD 개념 관계를 학문적으로 완벽하게 그리는 것이 아니라,
**"기출에 실제로 나온 개념을 빠뜨리지 않으면서, 무엇을 먼저 공부하고 그 다음 무엇을 공부해야 하는지"**를
보여주고, 각 개념에서 시험에 필요한 비교·함정·DBMS 차이를 바로 확인하게 하는 것입니다.

구현 전 데이터 검사 결과와 설계 계획은 [PLANNING.md](PLANNING.md)에 있습니다.

---

## 실행 방법

```bash
pip install networkx openpyxl            # Python 3.10+
python3 scripts/build_learning_graph.py  # data/*.json, web/data.js 생성 + 검증
python3 scripts/validate_graph.py        # (선택) JSON만으로 독립 재검증
```

웹앱은 빌드가 만든 `web/data.js` 번들을 읽으므로 서버 없이 열 수 있습니다.

```bash
open web/index.html                      # 또는 브라우저로 파일을 직접 열기
# 서버로 열고 싶다면
python3 -m http.server 8000              # → http://localhost:8000/web/
```

특정 Concept으로 바로 열기: `web/index.html#계층형 질의`

### 빌드 완료 시 출력 (현재 데이터 기준)

```
Total source concepts: 475
Current concepts: 286
Legacy-only concepts: 185
Learning DAG nodes: 491
Explicit prerequisite edges: 11
Inferred prerequisite edges: 644
Hierarchy edges: 916
Is DAG: True
Number of weakly connected components: 1
Orphan concepts: 0
Current concepts not included in DAG: 0
Mindmap-gap concepts not included in DAG: 0

  (Learning DAG nodes breakdown: source_concepts=475, dialect_reference_nodes=3, synthetic_structure_nodes=4, synthetic_integration_nodes=9)
  (Weakly connected components, concept-only prerequisite graph: 6; standalone cluster-root concepts: 3)
  (Legacy-only shown as support / hidden by default: 39 / 146)
  (Priority distribution: {'C': 50, 'B': 183, 'Legacy': 146, 'A': 112})

All 28 validation checks passed.
```

- **Learning DAG nodes 491** = 원본 Concept 475 + 원본 DIALECT 참조 노드 3(ANSI/ISO SQL, Oracle SQL, SQL Server) + 합성 노드 13(구조 4, Stage 9 통합 9).
- **Weakly connected components 1** 은 Stage backbone과 Cluster root anchor를 포함한 learning graph 기준입니다.
  Concept끼리의 prerequisite edge만 보면 6개 덩어리(3단계 스키마 묶음, DIALECT 참조 노드 3개, Legacy 파티셔닝 묶음)가 있으며,
  이들은 억지 edge를 만들지 않고 소속 Cluster root 아래에 배치했습니다.
- **Orphan concepts 0** 은 모든 Concept이 어떤 Stage root에서든 도달 가능하다는 뜻입니다.

---

## 폴더 구조

```
sqld-learning-dag/
  SQLD_knowledge_graph_v0_4.xlsx   원본 (입력)
  PLANNING.md                      구현 전 데이터 검사·설계 요약
  scripts/
    build_learning_graph.py        XLSX → 정규화 JSON → 검증 → web/data.js
    validate_graph.py              JSON만으로 독립 재검증 (exit code ≠ 0 이면 실패)
    curation/
      structure.py                 명시 edge 검토 결과, Cluster 재배치, 합성 노드, 표시 tier
      prerequisites.py             inferred prerequisite 목록 (edge마다 reason)
      content*.py                  definition / core rule / exam trap / example / 검색 alias
      comparisons.py               시험 비교 카드 37개
      dialects.py                  ANSI / Oracle / SQL Server 차이 28개
  data/
    nodes.json                     노드 + 메타데이터(Stage·Domain·Cluster·회차수·마인드맵·Priority·Legacy…)
    prerequisite_edges.json        Learning DAG edge (explicit + inferred)
    inferred_edges.json            그중 inferred만 (reason 포함)
    hierarchy_edges.json           Stage→Cluster→Concept→하위 Concept (선수관계 아님)
    metadata_relations.json        CONTRASTS·AFFECTS·DIALECT*·IS_A·허브 링크 등 (DAG 아님)
    rules.json                     Concept별 {definition, why_it_matters, core_rule, exam_traps, comparisons, dialect_notes, examples}
    comparisons.json / dialects.json
    stages.json                    Stage·Cluster·Domain·허브(20_Hubs_Rules)·gap family(04)
    legacy_nodes.json              11_Legacy_Only 185개와 기본 화면 표시 여부
    evidence.json                  Concept별 회차 증거(03_Round_Concepts)
    validation_report.json         검증 결과 전체
    cycle_report.json              cycle 검사 결과(검토 전 후보 그래프 포함)
  web/
    index.html, style.css, app.js  외부 라이브러리 없는 정적 웹앱
    data.js                        빌드 산출물 (data/*.json 번들)
```

---

## 1. 왜 전체 SQLD 관계를 DAG로 만들지 않았는가

`17_KG_Edges`에는 625개 typed relation이 있지만, 그중 519개는 계층(BELONGS_TO)이고 나머지 대부분은
**대조(CONTRASTS), 영향(AFFECTS), 방언(DIALECT_OF), 분류(IS_A)** 입니다.
이 관계들은 "무엇을 먼저 배워야 하는가"에 대한 답이 아닙니다.

- `RANK ↔ DENSE_RANK`, `COMMIT ↔ ROLLBACK`, `DELETE ↔ TRUNCATE ↔ DROP`처럼 **대칭인 관계**를 방향 간선으로 넣으면
  즉시 cycle이 생깁니다. `cycle_report.json`의 `diagnostic_naive_all_typed_relations`에 실제로 넣어 본 결과가 있습니다:
  원본 typed relation을 전부 방향 간선으로 넣으면 **DAG가 아니며**, 발견된 cycle 13개가 모두 CONTRASTS(12) 또는
  DIALECT_EQUIVALENT(1)의 대칭 간선을 포함합니다(예: `RANK → DENSE_RANK → RANK`, `WHERE → GROUP BY → HAVING → WHERE`).
- `NULL AFFECTS AVG`는 "AVG를 배우려면 NULL을 먼저 알아야 한다"가 아니라 "AVG 문제에 NULL 함정이 있다"는 뜻입니다.
- 모든 관계를 edge로 그리면 노드 하나에 수십 개의 선이 붙어 학습 순서가 보이지 않습니다.

그래서 화면의 본체는 **선수관계만 남긴 DAG** 이고, 나머지 관계는 노드 상세 패널의 카드/목록으로 보여줍니다.

## 2. Learning DAG의 edge 기준

edge의 방향은 항상 `prerequisite → next concept`, 질문은 하나입니다.
**"이 Concept을 이해하기 전에 무엇을 알아야 하는가?"**

### 명시 edge (원본 `17_KG_Edges`)

후보는 `REQUIRES`, `PRECEDES`, `ENABLES`, `EXPLAINS` 13개뿐입니다. 하나씩 검토해
**11개를 채택**(GROUP BY→HAVING은 PRECEDES와 REQUIRES가 겹쳐 1개로 병합)했습니다.

| 검토 결과 | edge | 이유 |
|---|---|---|
| 채택 | WHERE→GROUP BY, GROUP BY→HAVING, SELECT→ORDER BY | 학습 순서와도 일치 |
| 채택 | SELECT→ORDER BY 별칭, SQL 논리 실행 순서→SELECT 별칭 WHERE 사용 불가 / ORDER BY 별칭 | 규칙을 설명하는 선수 지식 |
| 채택 | OUTER JOIN 조건 위치→ON vs WHERE, 함수적 종속→2NF/3NF, NOCYCLE→CONNECT_BY_ISCYCLE, SAVEPOINT→ROLLBACK TO SAVEPOINT | 실제 선수 의미 |
| **재분류** | **HAVING PRECEDES SELECT** | 근거가 '논리적 실행 순서'. 평가 순서이지 학습 순서가 아님 → `SQL 논리 실행 순서`의 execution_order metadata로 이동 |

### Cycle 처리 (`cycle_report.json`)

edge를 임의로 지우지 않았습니다. 명시 후보 전부 + inferred edge로 만든 **후보 그래프**에서
`networkx.is_directed_acyclic_graph`가 `false`였고, 다음 cycle이 기록되었습니다.

```
GROUP BY → HAVING → SELECT → WHERE → GROUP BY
GROUP BY → HAVING → SELECT → 집계 함수 → GROUP BY
```

의심 edge 목록(`suspected_edges`) 중 prerequisite 관계만 다시 검토한 결과, 원인은 실행 순서를 학습 순서로 읽은
`HAVING PRECEDES SELECT` 하나였고 이것만 metadata로 재분류했습니다. 최종 Learning DAG는 `is_dag: true`입니다.
CONTRASTS·DIALECT 관계는 처음부터 후보에 들어가지 않으므로 cycle의 원인이 될 수 없습니다.

### Stage backbone과 anchor

- `18_Learning_DAG`의 '선수 단계'(예: Stage 4 ← Stage 2–3, Stage 9 ← Stage 0–8)를 Stage 노드 간 backbone edge로 사용합니다.
- prerequisite가 하나도 없는 Concept은 억지 edge를 만들지 않고 **소속 Cluster root 아래에 배치**(anchor edge)합니다.
- 검증: 모든 prerequisite edge가 `선수 Stage ≤ 다음 Stage`를 만족하는지(Stage 단조성) 확인합니다.

## 3. comparison / dialect / trap을 edge와 분리한 이유

| 원본 관계 | 화면에서의 위치 |
|---|---|
| CONTRASTS | **시험 비교 카드** (`comparisons.json`, 37개) — 예: RANK vs DENSE_RANK vs ROW_NUMBER, DELETE vs TRUNCATE vs DROP, WHERE vs HAVING, UNION vs UNION ALL, INNER vs OUTER, COUNT(*) vs COUNT(col), PK vs UNIQUE, 식별 vs 비식별, MINUS vs EXCEPT, ROWNUM vs TOP vs FETCH FIRST, NVL vs COALESCE, Oracle vs SQL Server NULL 정렬 … |
| DIALECT / DIALECT_OF / DIALECT_EQUIVALENT | **DBMS differences 표** (`dialects.json`, 28개 주제: ANSI / Oracle / SQL Server) |
| AFFECTS / EXCEPTION | **Exam traps** 와 '관련 개념' 목록 |
| IS_A / USES / IMPLEMENTS / ENFORCES / … | '관련 개념' 목록 (필요한 경우 별도 근거로 inferred edge를 둠, 아래 참조) |
| 20_Hubs_Rules Linked Concepts | 허브 카드 + HUB_LINK 관련 개념 |

이유:

1. **비교는 순서가 아니다.** RANK와 DENSE_RANK는 둘 다 `순위 함수` 다음에 오는 형제이고, 시험은 둘의 *차이*를 묻습니다.
   그래서 `윈도우 함수 → OVER 절 → PARTITION BY → 순위 함수 → {RANK, DENSE_RANK, ROW_NUMBER}`로 배치하고,
   차이는 각 노드 상세 패널의 카드(`1,2,2,4 / 1,2,2,3 / 1,2,3,4`)로 보여줍니다.
2. **방언은 같은 개념의 다른 표기다.** `MINUS`와 `EXCEPT`는 선후 관계가 아니라 같은 차집합의 이름 차이입니다.
3. **함정은 규칙 단위다.** 시험 문제는 Concept 이름보다 규칙(`NOT IN (…, NULL)`은 0행)을 묻기 때문에
   `rules.json`에 Concept별 `core_rule / exam_traps / examples`로 따로 둡니다.

대칭/방언 관계와 **같은 쌍**에 inferred edge가 걸린 경우는 소수이며, 그때도 edge는 대칭 관계가 아니라 별도의 선수 근거로 정당화됩니다
(예: `INNER JOIN → OUTER JOIN` — "OUTER JOIN = INNER 결과 + 비매칭 보존 행", `정규화 → 반정규화` — "반정규화는 정규화된 모델을 조정").
각 edge의 `related_source_relations` 필드에 겹치는 원본 관계가 기록되어 있습니다.
`UNION ↔ UNION ALL`처럼 순서가 아닌 대조 관계는 edge 없이 형제로 두고 비교 카드로만 표현합니다.

## 4. Current와 Legacy의 구분

| 구분 | 기준 (원본 시트) | 수 | 기본 화면 |
|---|---|---:|---|
| Current | `10_Current_Evidence` — 52회 이후 현행 기출에서 확인 | 286 | 표시 |
| Legacy-only | `11_Legacy_Only` — 52회 이후 증거 없음 | 185 | 아래 참조 |
| └ 보조(support) | Legacy-only 중 **현행 Concept의 선수/상위 개념** | 39 | 표시 (Priority C, 점선 테두리) |
| └ 숨김 | 그 외 (D7 성능·옵티마이저·분산 DB·PL/SQL·물리 조인 전부 포함) | 146 | **Include Legacy**로만 표시 |
| 참조 | 증거 없는 강의계획/구조 노드(PIVOT·UNPIVOT, IN·NOT IN …) + DIALECT 3 | 7 | 표시 (Priority C) |

Legacy 185개는 삭제하지 않습니다. 다만 `SELECT`, `JOIN`, `OUTER JOIN`, `식별자`, `INSERT`, `WITH 절`, `CTE`처럼
**현행 Concept을 이해하는 데 반드시 필요한 구범위 전용 Concept**을 숨기면 학습 경로가 끊기므로
(예: `LEFT OUTER JOIN`은 현행인데 `OUTER JOIN`은 구범위 전용), 이런 39개는 Priority C 보조 노드로 기본 화면에 남깁니다.
현행 범위 밖(`LEGACY`, D7 등) 노드는 보조로 쓰이지 않는다는 것도 검증합니다.

숨겨진 노드가 있는 Cluster에는 "Legacy n개 숨김"이 표시되고, 검색·하위 Concept 목록에서는 Legacy 배지와 함께 항상 찾을 수 있습니다
(예: `계층형 질의` 검색 시 `SYS_CONNECT_BY_PATH`가 Legacy 배지로 나타남).

### Priority (중심성·degree를 쓰지 않음)

| Priority | 규칙 | 수 |
|---|---|---:|
| A | 현행 2회 이상 **그리고** (다른 현행 Concept의 직접 선수 **또는** 시험 함정 2개 이상 **또는** 비교 카드 대상), 또는 현행 4회 이상. Stage 9 통합 노드는 선수 중 A가 2개 이상이면 A | 112 |
| B | 현행 출제 확인, A 조건 미충족 | 183 |
| C | 현행 증거 없음이지만 구조적으로 필요(보조 Legacy, 참조, 합성 구조 노드) | 50 |
| Legacy | 기본 숨김 | 146 |

각 노드의 `priority_reasons`에 판정 근거가 문장으로 들어 있습니다.

## 5. inferred prerequisite의 생성 기준

원본에 Concept 단위 선수관계가 13개뿐이라 대부분은 추론이 필요합니다.
`scripts/curation/prerequisites.py`에 **사람이 읽고 검토할 수 있는 목록**으로 작성했고, 빌드는 이 목록 밖의 edge를 만들지 않습니다.

- **명백한 학습 선수관계만** 추가합니다. 예:
  - `윈도우 함수 → OVER 절 → 순위 함수 → RANK` — "RANK는 윈도우 함수의 OVER(ORDER BY) 문맥을 전제로 하는 순위 함수"
  - `함수적 종속 → 부분 함수 종속 → 2NF` — "부분 함수 종속 개념을 알아야 2NF를 판별할 수 있음"
  - `UNKNOWN → NOT IN` — "NOT IN의 결과는 UNKNOWN(3값 논리)과 WHERE가 TRUE만 통과시키는 규칙으로 설명됨"
  - `인라인 뷰 → ROWNUM` — "ROWNUM은 ORDER BY 이전에 부여되므로 정렬 후 Top-N에는 인라인 뷰가 필요"
- 모든 inferred edge는 `"inferred": true`와 `reason`을 가집니다(검증 항목).
- **semantic similarity, 공동 출제, degree로 edge를 만들지 않습니다.** 이름이 비슷하다는 이유로 연결하지 않습니다.
- 원본 계층(BELONGS_TO)의 부모→자식도 자동으로 edge가 되지 않습니다. 부모 개념이 실제로 선수일 때만 이유와 함께 적었습니다.
- 명시 edge와 같은 쌍을 적은 경우는 명시 edge로 병합하고 `curated_reason`만 추가합니다.

### 원본을 보정한 곳 (모두 데이터에 기록)

- **Cluster 재배치 21건** (`nodes.json`의 `placement_override`): 선수관계가 뒤 Stage → 앞 Stage로 역행하지 않도록.
  예: `CHECK·UNIQUE·제약조건·NOT NULL`(Stage 2 SQ1 → Stage 7 MG3), `개체/참조 무결성`(Stage 0 DM0 → Stage 1 DM7),
  `GROUP BY NULL`(Stage 2 → Stage 5), `Oracle DDL 자동 커밋`(Stage 7 → Stage 8).
- **계층 2-cycle 해소 1건**: 원본 BELONGS_TO가 `정규표현식 ↔ 정규표현식 함수`를 서로의 부모로 가리킴.
- **합성 노드 13개** (`synthetic: true`, 근거 `synthetic_basis`):
  - 구조 4: `순환 관계(자기참조)`, `OVER 절`, `순위 함수`, `행 순서 함수` — 사용자 예시 경로에 필요한 경유 노드
  - Stage 9 통합 9: `NULL 처리 / NULL 정렬 / Top-N / 차집합 / DDL 커밋 / 문자열 함수 DBMS 차이`,
    `별칭 가시성 / NULL 함정 / OUTER JOIN 필터 위치 종합` — 원본 Stage 9가 비어 있어
    `04_Mindmap_Gaps`의 gap family를 근거로 추가

---

## 웹앱 기능

| 요구사항 | 구현 |
|---|---|
| Stage별 접기/펼치기 | Stage 헤더 클릭, 상단 `Stage 접기` |
| Cluster별 접기/펼치기 | Cluster 헤더 클릭(접기), `+n 세부` / `핵심만` |
| 초기 화면 | Stage → Cluster → 핵심 Concept(153개)만. 세부·Legacy는 펼치거나 Concept 클릭 시 표시 |
| Concept 검색 | 이름·별칭·정의 검색, 최상위 결과의 '연결 개념' 트리(하위/다음/관련) 표시. `/` 단축키 |
| Current Only / Include Legacy | 상단 토글 |
| 아직 공부하지 않은 Concept 표시 | `강조: 아직 공부하지 않은 Concept`, `지금 공부할 수 있는 Concept`(선수 모두 완료), `복습 필요` |
| 공부 완료 체크 | Concept 왼쪽 원 클릭(또는 Space), 상세 패널에서 4단계 상태 |
| 선수 미완료 표시 | Concept 칩의 `선수 n`, 상세 패널 경고(미완료 선수 목록) |
| 노드 클릭 시 상세 패널 | Definition · Why it matters · Prerequisites(edge 근거) · Next concepts · 하위 Concept · Core rules · Exam traps · 시험 비교 카드 · DBMS differences · 관련 개념(DAG 아님) · Examples · 현행/구범위 기출 근거(회차·출처) |
| 학습 경로 | `학습 경로` 탭: 기본 Stage 경로 + 선택 Concept까지의 최단 선수 경로(DAG 조상, 위상 정렬) + 그 Concept을 마무리하는 하위 학습. `캔버스에서 경로 강조` |

- 학습 상태는 `not_started / studying / learned / review_needed` 4가지이며 브라우저 `localStorage`에 저장됩니다.
  상단 `⋯` 메뉴에서 JSON으로 내보내기/가져오기/초기화할 수 있습니다.
- **부모 Concept을 배웠다고 하위 Concept을 자동으로 learned 처리하지 않습니다.**
- 화살표: 실선 = 직접 선수, 점선 = 숨겨진 세부 Concept을 거친 선수. 그리기는 transitive reduction으로 중복 화살표를 줄입니다
  (데이터의 edge는 그대로). 선택한 Concept의 다른 Cluster 선수/다음 Concept은 파란/빨간 점선과 테두리로 강조됩니다.
- 다크 모드, 모바일(폭 390px) 레이아웃을 지원합니다.

### 검색 예

- **NULL** → 연결 개념: UNKNOWN, NULL 비교, IS NULL, WHERE, IN·NOT IN / NOT IN / IN + NULL, COUNT / COUNT(열), AVG, GROUP BY NULL,
  DISTINCT NULL, OUTER JOIN, NVL, COALESCE, NULLIF, 빈 문자열과 NULL(Oracle), NULL 정렬, NULL 함정 종합 …
- **계층형 질의** → START WITH, CONNECT BY, PRIOR, LEVEL, ORDER SIBLINGS BY, NOCYCLE, CONNECT_BY_ISLEAF, CONNECT_BY_ISCYCLE,
  CONNECT_BY_ROOT, SYS_CONNECT_BY_PATH(Legacy), 순방향/역방향 계층 전개, WHERE 후필터, 재귀 CTE …
- **계층형 질의까지 학습 경로** → 엔터티 → 관계 → 순환 관계(자기참조) → 식별자 → … → PK → FK → SELECT → 테이블 별칭 → WHERE → JOIN →
  셀프 조인 → **계층형 질의**, 이어서 START WITH → CONNECT BY → PRIOR / LEVEL / NOCYCLE / ORDER SIBLINGS BY …

---

## 검증 항목 (`validate_graph.py`)

오류(error)로 처리하는 항목: DAG 여부(Concept DAG, anchor 포함 learning graph), cycle_report 일치, 명시 edge 관계 타입 제한,
금지 관계(CONTRASTS·AFFECTS·DIALECT*·EXCEPTION·IS_A·IMPLEMENTS) 미사용, inferred edge의 reason, 중복/self-loop 없음,
Stage 단조성, 원본 수(475/286/185/191) 일치, orphan 없음, Current·gap Concept의 DAG 포함 및 기본 화면 표시,
기본 화면 노드의 선수가 숨겨지지 않음, D7 Legacy 기본 숨김, 계층 cycle 없음, 카드 참조 유효, 단일 연결 요소.
경고(warning): definition 누락, Priority A의 규칙/함정 누락, 허브 링크 미해석.

## 한계

- 복원 기출은 공식 원문이 아니므로 회차 수는 "Concept 존재 증거"입니다(원본 `00_Summary` 주의사항과 동일).
- inferred edge와 규칙·함정 텍스트는 사람이 작성한 큐레이션입니다. 틀린 곳이 있으면 `scripts/curation/`을 고치고 다시 빌드하세요.
  빌드가 이름 오타, cycle, Stage 역행을 잡아냅니다.
