# SQLD 개념 구조 · 학습 DAG

`SQLD_knowledge_graph_v0_5_with_content.xlsx`(source of truth)로 만든 SQLD 시험 대비 웹앱입니다.

| 화면 | 답하는 질문 |
|---|---|
| **개념 구조** (Concept Structure DAG) | SQLD 지식이 어떻게 구성되어 있는가? — SQLD › Domain › Cluster › Concept |
| **학습 순서** (Learning DAG) | 무엇을 먼저 배우고, 그 다음 무엇을 배우는가? — 선수 → 다음 |
| **Concept 상세** | 시험에서 이 개념으로 무엇을 알아야 하는가? — Overview · Learn · Exam · SQL · DBMS |

통합 계획과 repository 조사 결과: [`../docs/sqld-dag-integration-plan.md`](../docs/sqld-dag-integration-plan.md)
v0.4 단계의 데이터 검사 기록: [PLANNING.md](PLANNING.md)

---

## 실행

```bash
pip install networkx openpyxl              # Python 3.10+
python3 scripts/build_learning_graph.py    # xlsx → data/*.json + web/data.js, 검증 결과 출력
python3 scripts/validate_graph.py          # (선택) JSON만으로 독립 재검증
```

`web/index.html`을 브라우저로 바로 열면 됩니다(빌드가 만든 `web/data.js` 번들 사용, 서버 불필요).
서버로 열려면 `python3 -m http.server 8000` → `http://localhost:8000/web/`. 특정 Concept 바로 열기: `web/index.html#RANK`.

### 테스트

```bash
python3 -m unittest discover -s tests -v   # 파이프라인·데이터 21개 (stdlib)
node --test tests/logic.test.mjs           # 검색·필터·펼치기·경로 로직 8개 (Node 내장 test runner)
node --test tests/ui_smoke.test.mjs        # (선택) 브라우저 스모크 — Playwright가 없으면 skip
```

추가 의존성은 없습니다(빌드와 같은 networkx/openpyxl, Node 내장 `node:test`).

---

## 데이터 원칙

### Source of truth = Excel

- **Node ID가 canonical ID**입니다. 이름은 표시용이며, 이름이 겹치는 Cluster/Concept(예: `엔터티`, `JOIN`)도 ID로 구분합니다.
- 학습 콘텐츠는 모두 Excel에서 읽습니다: `21_Concept_Content`(Definition, Why It Matters, Prerequisites, Core Rule,
  Syntax/Pattern, Exam Trap, Comparison Targets, Dialect Notes, **Content Depth**, **Review Flag**), `22_Rules_And_Traps`,
  `23_Comparisons`, `24_SQL_Examples`, `25_Dialect_Notes`. 원본 문구를 바꾸거나 다시 쓰지 않습니다(테스트로 확인).
- `CURATED`/`TEMPLATE`와 `우선검토` 플래그는 데이터에 그대로 보존되고 상세 패널에 작은 배지로 표시됩니다.
- 이전 단계(v0.4)에 제가 작성했던 보조 설명·비교표·방언표는 **삭제하지 않고 `supplementary_notes.json`으로 분리**했습니다.
  상세 패널에서 "보조 … — curated-v0.4 (Claude 작성 보조 노트 · 원본 아님 · 검토 필요)"라는 접힌 블록으로만 보입니다.

### 추론(inferred) 데이터

원본에 없는 것은 모두 `inferred: true` + `reason` + `confidence`로 따로 기록합니다(`data/inferred_edges.json`).

| 종류 | 수 | 내용 |
|---|---:|---|
| Learning inferred edge | 388 | 원본 explicit edge와 중복(255)·함의되는 것은 제외하고 남긴 선수관계. high 354 / medium 34 |
| Structure inferred edge | 26 | 학습용 그룹 노드(`순위 함수` 등) 소속. 원본 BELONGS_TO는 그대로 유지 |
| inferred 노드 | 13 | 구조 4(`OVER 절`, `순위 함수`, `행 순서 함수`, `순환 관계(자기참조)`), Stage 9 통합 9 |
| 학습 화면 배치 보정 | 22 | Stage가 역행하는 원본 배치를 **학습 순서 화면에서만** 보정(예: `CHECK` Stage 2 → 7). 개념 구조 화면은 원본 Cluster |
| 이름 alias | 1 | `25_Dialect_Notes`의 `ISNULL`(노드 없음) → `NVL` |

규칙: 학습 선수관계가 명백할 때만, semantic similarity·공동 출제로는 만들지 않음. **원본과 충돌하는 inferred edge는 버립니다**
(예: 원본 `정규화 → 이상현상`과 반대인 `이상현상 → 정규화`는 사용하지 않음 — `cycle_report.json`에 기록).

---

## 두 DAG

### A. Concept Structure DAG (`data/concept_structure_edges.json`)

- 노드 540 = ROOT 1 + Domain 7 + Cluster 41 + Concept 475 + DIALECT 3 + inferred 13
- edge 572 = `17_KG_Edges`의 BELONGS_TO + IS_A, 그리고 inferred PART_OF 26
- 원본 보정 2가지(모두 build notes·cycle_report에 기록):
  - `17`의 Domain→Cluster edge 14개가 **같은 이름 Concept의 ID**를 가리켜 Cluster 노드가 떨어져 있었음 → `16_KG_Nodes`의 Domain/Cluster 열(= `19_Study_Outline_v2` 경로)로 연결. 원본 edge는 삭제하지 않음
  - `정규표현식 ↔ 정규표현식 함수` BELONGS_TO 2-cycle → 검토 후 `정규표현식 → 정규표현식 함수`만 사용
- 결과: DAG ✓, Concept 누락 0, 현행 Concept 누락 0, orphan 0

### B. Learning DAG (`data/prerequisite_edges.json`)

- 노드 491 = Concept 475 + DIALECT 3 + inferred 13
- **explicit 396** = `21_Concept_Content.Prerequisites`의 Concept 토큰 ∪ `17`의 REQUIRES/PRECEDES/ENABLES/EXPLAINS. edge마다 `provenance`
- Prerequisites의 Cluster/Domain 이름(97개 토큰)은 Concept edge가 아니라 **학습 블록 소속**으로 해석합니다
- 재검토로 제외한 explicit 후보 2개(삭제하지 않고 `cycle_report.json`·`validation_report.json`에 보존):
  - `HAVING → SELECT`: 근거가 '논리적 실행 순서'라 학습 순서와 반대 → `SQL 논리 실행 순서`의 execution_order metadata로 이동
  - `정규표현식 함수 → 정규표현식`: 원본 상호참조 2-cycle
- **inferred 388**(위 표)
- 결과: DAG ✓, 현행 Concept 누락 0, 마인드맵 gap 누락 0. 선수가 없는 Concept 15개는 억지 edge 없이 학습 블록 root에 둡니다

### DAG에 넣지 않는 관계

CONTRASTS, AFFECTS, DIALECT, DIALECT_OF, DIALECT_EQUIVALENT, EXCEPTION, RELATED_TO, CO_OCCURS_WITH는 어느 DAG에도
방향 간선으로 넣지 않습니다. 진단용으로 원본 typed relation을 모두 방향 간선으로 넣어 보면 DAG가 깨지고(cycle 13개),
그 cycle은 전부 CONTRASTS·DIALECT_EQUIVALENT 대칭 간선 때문입니다(`cycle_report.json` → `diagnostic_naive_all_typed_relations`).
대신 비교는 **Comparison Card**(`23`), 방언은 **DBMS 탭**(`25`), 영향·함정은 **Exam 탭**에서 보여줍니다.

---

## 우선순위 · Current / Legacy

원본 evidence count(현행 52회 이후 / 구범위)를 그대로 보존하고, degree·centrality·출제확률은 쓰지 않습니다.

| Priority | 규칙 | 수 |
|---|---|---:|
| A | 현행 4회 이상, 또는 현행 2회 이상이면서 (현행 Concept의 직접 선수 · 원본 시험 함정 · 원본 비교 카드 중 하나) | 100 |
| B | 현행 출제 확인 | 195 |
| C | 현행 증거 없음이지만 구조적으로 필요(현행 Concept의 선수인 구범위 Concept 38개, 참조·inferred 구조 노드) | 49 |
| Legacy | `11_Legacy_Only` 중 C가 아닌 것 — 기본 숨김, **Include Legacy**로 표시 | 147 |

Legacy 185개는 모두 보존됩니다. 옵티마이저·실행계획·인덱스·PL/SQL·분산 DB·NL/Sort Merge/Hash Join·성능 데이터 모델링은 기본 화면에서 숨겨집니다.

---

## 웹앱 기능

- 상단: `개념 구조 | 학습 순서` 전환, Stage 필터, Domain 필터, 검색(`/`), Current Only / Include Legacy, 강조(미학습·지금 공부 가능·복습 필요), 핵심만 / 모두 펼치기 / 섹션 접기
- 초기 화면: 개념 구조는 Domain › Cluster › 핵심 Concept(134), 학습 순서는 Stage › 학습 블록 › 핵심 Concept(141). Cluster의 `+n 세부`나 Concept 클릭으로 하위·다음 Concept 표시
- 상세 패널 5탭
  - **Overview**: Definition, Why It Matters, 위치(개념 구조 경로 / 학습 Stage), Domain, Current/Legacy, 현행 출제 회차수, Content Depth·Review Flag, 하위 Concept, 연결된 Obsidian 노트
  - **Learn**: Prerequisites(출처 태그: `21 Prerequisites`, `17 PRECEDES`…, 또는 `inferred · confidence`), 원본 Prerequisites 텍스트, Next concepts, Core Rule, Syntax/Pattern, Rules(`22`)
  - **Exam**: Exam Traps(`22` EXAM_TRAP + `21` Exam Trap), Comparison Cards(`23`), 이 Concept을 링크하는 모의고사 문항(`Questions/*.md`), 현행·구범위 기출 근거
  - **SQL**: `24` 예제를 RESULT(Expected Result 포함) / SYNTAX로 구분
  - **DBMS**: `25` Oracle / SQL Server / ANSI 노트, `22` DIALECT_RULE
- 학습 상태 `not_started / studying / learned / review_needed`(localStorage, 기존 키 유지), 선수 미완료 표시, JSON 내보내기·가져오기. 부모를 배워도 하위를 자동 완료 처리하지 않음
- **학습 경로** 탭: 목표 Concept의 선수 조상을 **갈래 그대로** 미니 DAG로 표시 + 위상 순서 체크리스트 + 하위 마무리 학습. 캔버스 강조 가능

Obsidian vault(`Concepts/`, `Questions/`)는 읽기만 합니다. 노트 파일명이 Concept 이름과 같으면 연결하고, 모의고사 문항의 `[[wikilink]]`로 관련 문항을 찾습니다.

---

## 파일

```
sqld-learning-dag/
  SQLD_knowledge_graph_v0_5_with_content.xlsx   source of truth (v0.4 파일은 이력으로 보존)
  scripts/build_learning_graph.py               빌드 (두 DAG, 콘텐츠 연결, 검증 호출, data.js 번들)
  scripts/validate_graph.py                     독립 검증(42개 체크)
  scripts/curation/                             inferred edge·노드·배치, 보조 노트(v0.4)
  data/
    nodes.json                    노드 + 메타데이터(Stage·Domain·Cluster·회차수·마인드맵·Priority·Content Depth…)
    concept_structure_edges.json  Structure DAG (structure_nodes + edges)
    prerequisite_edges.json       Learning DAG (explicit + inferred, provenance/confidence)
    inferred_edges.json           inferred edge·노드·배치·alias
    content.json                  Concept별 21 콘텐츠 + 22/23/24/25 연결 ID
    rules_and_traps.json, comparisons.json, examples.json, dialects.json   22–25 원본 행
    supplementary_notes.json      v0.4 보조 노트(원본 아님)
    stages.json, legacy_nodes.json, evidence.json, metadata_relations.json, vault_links.json
    cycle_report.json             learning / structure 각각의 cycle·suspectedEdges·검토 결정
    validation_report.json        요약 + 세부 + 체크 결과
  web/  index.html · style.css · logic.js(순수 로직) · app.js(화면) · data.js(빌드 산출물)
  tests/  test_sqld_graph.py · logic.test.mjs · ui_smoke.test.mjs
```

## 한계

- 복원 기출은 공식 원문이 아니므로 회차 수는 "Concept 존재 증거"입니다.
- 현행 Concept 중 168개는 원본에서 `TEMPLATE` + `우선검토`입니다. 콘텐츠 보강은 Excel에서 하고 다시 빌드하세요.
- inferred edge와 보조 노트는 사람이 검토해야 할 큐레이션입니다. `scripts/curation/`을 고치면 빌드가 이름 오타·cycle·Stage 역행을 잡습니다.
