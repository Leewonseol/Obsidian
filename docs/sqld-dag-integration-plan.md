# SQLD 지식·학습 DAG 통합 계획 (v0.5 content)

입력: `SQLD_knowledge_graph_v0_5_with_content.xlsx` — 이 문서는 코드를 고치기 전에 repository와 workbook을 조사한 결과다.

## 1. 현재 repository architecture

| 영역 | 내용 |
|---|---|
| 성격 | Obsidian vault의 `SQLD/Pilot` 폴더를 Git으로 백업한 저장소 (`_config/README.md`) |
| 노트 데이터 | `Concepts/*.md` 59개(frontmatter: type, learning_tier, axis_membership …), `Questions/*.md` 50개(모의고사 문항, `[[개념]]` wikilink), `Propositions/*.md` 200개, `SQLD 학습 대시보드.md`, `_reports/` |
| 그래프 설정 | `_config/graph.json` — Obsidian 내장 그래프 뷰 설정 백업(colorGroups 등). 코드 아님 |
| 기존 SQLD 웹 기능 | `sqld-learning-dag/` (직전 작업, 브랜치 `claude/sharp-volta-e5yuay`) |
| └ data pipeline | `scripts/build_learning_graph.py` (openpyxl + networkx) → `data/*.json` + `web/data.js` 번들, `scripts/validate_graph.py` (독립 재검증), `scripts/curation/*.py` (사람이 쓴 inferred edge·보조 콘텐츠) |
| └ frontend | `web/index.html`, `web/app.js`, `web/style.css` — **프레임워크·라이브러리 없음**(vanilla JS + SVG). 레이아웃은 Cluster별 layered DAG |
| └ 상태관리/저장 | `app.js` 내부 `state` 객체, 학습 진행은 `localStorage` (`sqld-learning-dag:progress:v1`, not_started/studying/learned/review_needed), JSON 내보내기/가져오기 |
| package.json / pyproject / requirements | 없음 (Python: networkx, openpyxl 직접 설치) |
| 라우터 | 없음. 단일 페이지 + URL hash(`#개념명`)로 Concept 직접 열기 |
| graph library | 없음 (React Flow·Cytoscape·D3·vis-network 미사용). 자체 SVG 렌더러 |
| CSS | `web/style.css` — CSS 변수 토큰 + 다크모드, Tailwind/컴포넌트 라이브러리 없음 |
| test framework | 없음. 빌드 시 `validate_graph.py`가 28개 검증 수행 |
| build/deploy | 없음 (GitHub Pages/Vercel/Netlify 설정 없음). `web/index.html`을 파일로 열거나 `python3 -m http.server` |

## 2. Workbook 조사 결과

- `16_KG_Nodes`, `17_KG_Edges`, `18_Learning_DAG`, `19_Study_Outline_v2`, `20_Hubs_Rules`, `10/11/13`, `02`는 v0.4와 **완전히 동일**(diff 0). 새 시트는 21–26.
- `21_Concept_Content` 475행, Node ID/Concept 이름이 16과 1:1 일치. Content Depth: CURATED 136 / TEMPLATE 339. Review Flag: 우선검토 168 / Legacy 참고 185 / 빈칸 122.
- `21.Prerequisites` 토큰(쉼표 구분 — 이름에 `/`가 들어가므로 `/`로 자르면 안 됨): Concept 이름 398, Cluster 이름 78, Domain 이름 19.
  - Concept→Concept 398개 중 **385개는 BELONGS_TO 부모**와 같고, 13개는 17의 REQUIRES/PRECEDES/ENABLES/EXPLAINS·IS_A·IMPLEMENTS 관계와 같다.
  - Cluster/Domain 토큰은 Concept edge가 아니라 "학습 블록(Stage/Cluster) 소속"으로 해석한다.
  - 원본 자체에 **cycle 1개**: `정규표현식 ↔ 정규표현식 함수` (BELONGS_TO도 서로를 부모로 가리킴).
  - **`HAVING → SELECT`**(17의 PRECEDES, 근거 '논리적 실행 순서')가 21에도 들어 있다 — 학습 순서와 반대.
  - Stage가 역행하는 원본 edge 8개(예: `DDL(Stage 7) → DEFAULT(Stage 2)`, `ROUND(Stage 3) → 날짜 ROUND(Stage 2)`).
- `22_Rules_And_Traps` 555행: DEFINITION 475, CORE_RULE 40, EXAM_TRAP 31, DIALECT_RULE 6, COMPARISON_RULE 3. Node ID 참조 오류 0.
- `23_Comparisons` 24개(A vs B 쌍, 이름 참조) — 이름은 모두 해석됨.
- `24_SQL_Examples` 65개: SYNTAX 56, RESULT 9(Expected Result 포함). Node ID 참조 오류 0.
- `25_Dialect_Notes` 17개(이름 참조): `ISNULL`은 Concept 노드가 없음 → NVL 대응으로 alias 연결(inferred로 기록).
- `26_Content_Coverage`: 집계 KPI(검증 비교용).

## 3. 재사용할 기존 컴포넌트

| 기존 | 재사용 방식 |
|---|---|
| `build_learning_graph.py` | 같은 파일을 확장. 입력을 v0.5로 바꾸고 21–25 시트 파싱, 두 DAG 생성 |
| `validate_graph.py` | 같은 파일을 확장. Structure DAG / Learning DAG 각각 검증 + coverage 항목 추가 |
| `curation/structure.py` | 명시 edge 검토 결과(HAVING→SELECT, 정규표현식 2-cycle), 합성 노드, Learning 화면 배치 보정 — 모두 `inferred`·`reason`·`confidence`로 기록 |
| `curation/prerequisites.py` | 원본에 없는 선수관계만 inferred edge로 사용(원본 explicit edge와 중복·함의되는 것은 제외), 각 edge에 confidence 추가 |
| `curation/content*.py`, `comparisons.py`, `dialects.py` | **원본 콘텐츠를 대체하지 않음.** "보조 노트(원본 아님)"로 분리 저장하고 상세 패널에서 접힌 상태로만 표시 |
| `web/app.js` Cluster layered layout, 칩, SVG edge, 진행 상태, 검색, 경로 | 그대로 사용. 레이아웃 함수를 edge 종류(구조/학습)를 인자로 받도록 일반화 |
| `web/style.css` 토큰 | 그대로 사용, 필요한 클래스만 추가 |
| localStorage progress | 키·형식 그대로(기존 진행 상황 유지) |
| Obsidian 노트 | 읽기 전용으로 스캔: Concept 노트가 있는 노드와 그 노드를 `[[링크]]`하는 모의고사 문항을 상세 패널에 표시. 노트 파일은 수정하지 않음 |

## 4. 수정할 파일

- `sqld-learning-dag/scripts/build_learning_graph.py` — v0.5 입력, content 시트, Structure DAG, explicit/inferred 재정의, 출력 추가
- `sqld-learning-dag/scripts/validate_graph.py` — 두 DAG 검증, coverage, 참조 무결성
- `sqld-learning-dag/scripts/curation/structure.py`, `prerequisites.py` — 검토 결과·confidence
- `sqld-learning-dag/web/index.html`, `app.js`, `style.css` — [개념 구조]/[학습 순서] 뷰 탭, Stage/Domain 필터, 상세 패널 5탭(Overview/Learn/Exam/SQL/DBMS), 분기 그대로의 목표 경로 그래프
- `sqld-learning-dag/README.md`

## 5. 새로 만들 파일

- `docs/sqld-dag-integration-plan.md` (이 문서)
- `sqld-learning-dag/SQLD_knowledge_graph_v0_5_with_content.xlsx` (source of truth; v0.4 파일은 이력으로 남김)
- `sqld-learning-dag/web/logic.js` — DOM 없는 순수 로직(검색 순위, 표시 필터, 조상 계산, 레이어 배치). 브라우저와 Node 테스트가 공유
- `sqld-learning-dag/tests/test_sqld_graph.py` — Python `unittest`(추가 의존성 없음)
- `sqld-learning-dag/tests/logic.test.mjs` — Node 내장 `node:test`(추가 의존성 없음)
- data 출력(기존 `sqld-learning-dag/data/` 관례 유지): `concept_structure_edges.json`, `content.json`, `examples.json`, `rules_and_traps.json`, `supplementary_notes.json`, `vault_links.json` 추가. Learning DAG는 기존 파일명 `prerequisite_edges.json`을 유지(별도 `learning_edges.json`을 만들지 않음). `comparisons.json`·`dialects.json`은 **Excel 원본(23·25) 기반으로 재정의**, v0.4 `rules.json`·`hierarchy_edges.json`은 `content.json`·`concept_structure_edges.json`으로 대체

## 6. 데이터 변환 방식

브라우저는 XLSX를 파싱하지 않는다. 기존 build-time pipeline이 JSON과 `web/data.js`를 만든다.

1. **노드**: Node ID가 canonical ID(이름은 표시용). 16의 모든 노드(ROOT/DOMAIN/CLUSTER 포함)를 Structure DAG에 넣고, Concept 475 + DIALECT 3을 Learning DAG에 넣는다. 합성 노드(OVER 절·순위 함수 등)는 `inferred: true, reason, confidence`로 별도 ID(X…)를 가진다.
2. **Concept Structure DAG**: 17의 BELONGS_TO(SQLD→Domain→Cluster→Concept→하위) + IS_A. 원본 2-cycle은 report 후 검토 결정(정규표현식을 상위로)만 적용. 합성 그룹 노드(순위 함수 등)는 inferred PART_OF edge로 추가하되 원본 BELONGS_TO edge도 유지.
3. **Learning DAG**:
   - explicit = `21.Prerequisites`의 Concept 토큰 ∪ 17의 REQUIRES/PRECEDES/ENABLES/EXPLAINS. 출처(`21_Concept_Content.Prerequisites`, `17_KG_Edges:<relation>`)를 edge에 기록.
   - 후보 그래프에서 cycle을 먼저 기록(`cycle_report.json`) → prerequisite 관계만 검토: `HAVING→SELECT`(실행 순서) metadata로 재분류, `정규표현식 함수→정규표현식`(원본 상호참조) 제외. 삭제가 아니라 `excluded_explicit_edges`로 보존.
   - inferred = curated 목록 중 explicit에 없고 explicit 경로로 이미 함의되지 않는 edge만, `confidence`(high/medium)와 `reason` 포함.
   - Cluster/Domain 토큰은 학습 블록 소속(root-level learning node)으로 사용. 억지 edge 없음.
4. **금지 관계**(CONTRASTS, AFFECTS, DIALECT*, EXCEPTION, RELATED_TO, CO_OCCURS_WITH)는 두 DAG 어디에도 넣지 않고 metadata/카드로.
5. **콘텐츠**: 21(정의·Why·Core Rule·Syntax·Exam Trap·Comparison Targets·Dialect Notes·Content Depth·Review Flag), 22(rule 행), 23(비교 카드), 24(예제), 25(방언)를 Node ID로 연결. 이름 참조(23/25)는 이름→ID 해석, 실패는 validation에 보고.
6. **우선순위**: 원본 evidence count 보존. Priority는 현행 회차수 + 선수 여부 + 원본 함정/비교 존재만으로 계산(degree·centrality·확률 계산 없음).
7. **Learning 화면 배치 보정**: Stage가 역행하는 원본 배치(CHECK·DEFAULT가 Stage 2 등)는 원본 cluster/stage를 그대로 보존하고, 학습 화면용 배치만 `inferred_placements`로 보정(reason·confidence). Structure DAG는 원본 배치를 그대로 쓴다.

## 7. DAG UI 통합 위치

기존 `sqld-learning-dag/web/index.html` 한 화면 안에서:

- 상단 바에 뷰 전환 `[개념 구조] [학습 순서]` 추가(새 내비게이션 시스템 없음, 기존 segmented control 스타일 재사용)
- `Stage` / `Domain` 필터 select 추가, 기존 검색·Current/Legacy 토글·강조·펼치기 버튼 유지
- **개념 구조**: Domain 섹션 → Cluster 카드 → 핵심 Concept 트리(클릭/펼치기 시 하위)
- **학습 순서**: 기존 Stage 섹션 → Cluster(학습 블록) 카드 → 핵심 Concept layered DAG
- 상세 패널: `상세`(Overview / Learn / Exam / SQL / DBMS 하위 탭) + `학습 경로`(목표 Concept의 선수 조상 서브그래프를 **분기 그대로** 그리는 미니 DAG + 체크리스트)

## 8. 기존 기능과 충돌 가능성

| 위험 | 대응 |
|---|---|
| 기존 진행 상황(localStorage) | 키·형식·Node ID 불변 → 그대로 유지. 합성 노드 ID(X…)도 그대로 |
| v0.4 큐레이션 콘텐츠와 Excel 콘텐츠 충돌 | Excel이 우선. 큐레이션은 "보조 노트(원본 아님)"로 접어서만 표시, 데이터에 `source: curated-v0.4` |
| Learning edge 수·우선순위 변화 | 의도된 변화. validation_report에 이전 정의와 함께 수치 기록 |
| Obsidian vault | `docs/` 폴더가 vault에 노트로 보일 수 있음(마크다운 1개). 기존 노트·`_config`는 읽기만 함 |
| 브랜치 | 기존 작업 브랜치 `claude/sharp-volta-e5yuay`에 이어서 커밋 |

## 9. 추가 dependency

없음. Python은 기존과 같은 `networkx`, `openpyxl`, 테스트는 stdlib `unittest`, JS 테스트는 Node 내장 `node:test`.
UI 스모크 테스트(Playwright)는 저장소에 의존성을 추가하지 않고 개발 환경에서만 실행한다.

## 10. 구현 중 추가로 발견해 반영한 점

- `17_KG_Edges`의 Domain→Cluster BELONGS_TO 14개가 같은 이름의 **Concept ID**를 가리켜 Cluster 노드가 고립되어 있었다
  (`엔터티`, `JOIN`, `윈도우 함수` 등). 원본 edge는 그대로 두고 `16_KG_Nodes` Domain/Cluster 열(= `19_Study_Outline_v2` 경로)로 Cluster를 연결했다.
- v0.4 inferred edge `이상현상 → 정규화`가 원본 explicit `정규화 → 이상현상`(21 Prerequisites)과 cycle을 만들었다.
  source of truth를 따라 inferred 쪽을 버리고 `cycle_report.json`에 기록했다(원본과 충돌하는 inferred edge는 자동으로 거부하는 규칙 추가).
- `25_Dialect_Notes`의 `ISNULL`은 Concept 노드가 없어 `NVL`에 alias로 연결(inferred, reason·confidence 기록).
- 검색에서 `ISNULL`이 `IS NULL`과 같은 문자열로 정규화되던 문제를 테스트로 발견해, 공백을 보존한 정확 일치를 우선하도록 수정했다.
