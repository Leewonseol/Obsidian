---
type: report
status: 3차 단계(Hub 4개 → Concepts/ 폴더 이동 + type: concept 전환) 이후 검증
---

# 4대축 Concept 노드 전환 검증

## 0. 배경

1차 단계에서 4개 파일(`Hubs/`)에 `type: hub` + `exclude_from_centrality: true`를 부여했고, 2차 단계에서 54개 Concept의 axis_membership frontmatter와 Hub 4개를 신설했다(검증: `4대축-2차수정후-검증.md`). 이번 3차 단계는 그 두 산출물과 다른 방향으로, "Hub는 탐색용 색인일 뿐 실제 학습 연결망 노드가 아니다"라는 기존 구조를 폐기하고, 4개 파일을 `Concepts/` 폴더로 이동해 **실제 Concept 노드**로 편입하는 작업이다. 직전에 시도된 `type: axis` 전환(별도 Hub/Axis 계층 유지 방식)은 사용자가 취소했으며, 이번 보고서는 그 취소 이후 새로 지시된 최종 명세(`type: concept` + `concept_kind: structural_axis` + 폴더 이동)를 기준으로 한다.

## 1. 이동된 파일 4개

| 기존 경로 (Hubs/) | 새 경로 (Concepts/) | axis_id |
|---|---|---|
| 데이터 모델링에서 JOIN까지.md | Concepts/데이터 모델링에서 JOIN까지.md | modeling_to_join |
| SQL 작성 순서.md | Concepts/SQL 작성 순서.md | sql_writing_order |
| SQL 논리적 실행 순서.md | Concepts/SQL 논리적 실행 순서.md | sql_execution_order |
| Oracle과 SQL Server 차이.md | Concepts/Oracle과 SQL Server 차이.md | oracle_sqlserver |

4개 파일 모두 본문(흐름 설명, 소속 Concept 목록, 위키링크)은 전혀 수정하지 않았다. frontmatter만 다음 구조로 교체했다.

```
---
type: concept
concept_kind: structural_axis
axis_id: <기존 axis_id 유지>
graph_role: structural_axis
include_in_learning_graph: true
exclude_from_concept_centrality: true
---
```

`Hubs/` 폴더 자체는 삭제하지 않았다(파일이 빠져나가 빈 폴더로만 남음 — 지시에 폴더 삭제 항목이 없어 그대로 유지).

## 2. type: concept 파일 총수

`Concepts/*.md` 전체를 대상으로 `type: concept` 라인을 재확인한 결과 **58개** 전부 일치한다(atomic 54 + structural_axis 4).

## 3. atomic concept 수 / structural_axis concept 수

- **atomic concept**: 54개 (`concept_kind` 필드 없음, 기존 54개 파일 — 이번 단계에서 수정하지 않음)
- **structural_axis concept**: 4개 (`concept_kind: structural_axis`가 붙은 이동된 파일 4개)

## 4. 학습 연결망(Learning Graph) 노드·엣지 수

- **노드 수**: 58 (atomic 54 + structural_axis 4)
- **엣지 수**: 172
  - concept↔concept (atomic 54개 사이, 기존 baseline): 95
  - structural_axis → atomic concept (각 축 본문의 "소속 Concept 목록"에 실제 존재하는 위키링크만 집계): 76
    - 데이터 모델링에서 JOIN까지: 23
    - SQL 작성 순서: 34
    - SQL 논리적 실행 순서: 14
    - Oracle과 SQL Server 차이: 5
  - structural_axis ↔ structural_axis: 1 (SQL 작성 순서 ↔ SQL 논리적 실행 순서, 상호 참조)

축→개념 엣지는 각 파일의 "소속 Concept 목록 (N개)" 절에 실제 존재하는 위키링크만 집계했으며, 코드블록 안에서만 등장하고 목록/본문에 재등장하지 않는 링크는 없었다(4개 파일 모두 코드블록 내 위키링크가 목록 절에 중복 등장). FROM·SELECT처럼 대응하는 atomic Concept 파일이 없는 흐름 요소는 지시대로 새 Concept를 만들지 않았고, 따라서 엣지도 생성하지 않았다.

## 5. 중심성 계산 대상 노드 수

**54개** (atomic concept만). `concept_kind: structural_axis`인 4개는 `exclude_from_concept_centrality: true`로 표시되어 있으며, 이번 단계에서 atomic concept 54개 파일의 본문·frontmatter를 전혀 건드리지 않았으므로 이 54개 사이의 위키링크 집합(95 엣지)은 물리적으로 변할 수 없다.

## 6. 기존 중심성 순위 유지 여부

**유지됨.** 근거:
- 이동/수정된 4개 파일은 원래도 atomic Concept 54개에 포함되지 않았다(1차 단계부터 `Hubs/`에 별도로 존재).
- 이번 3차 단계에서 54개 atomic Concept 파일은 1바이트도 수정하지 않았다(수정 대상은 이동된 4개 파일의 frontmatter뿐).
- 따라서 `4대축-균형중심성.csv`·`.md`(1차 baseline)와 `4대축-2차수정후-검증.csv`(2차 검증)가 보고한 54개 순위·centrality·min·geomean·betweenness 수치는 이번 단계 이후에도 텍스트 수준에서 완전히 동일하다. 두 보고서 모두 이번 단계에서 수정하지 않았다.

## 7. 깨진 링크 수

**0건.**
- 이동된 4개 파일이 참조하는 모든 위키링크(23+34+14+5개 목록, 중복 제외)를 `Concepts/` 폴더의 실제 파일명과 대조해 전부 존재함을 확인했다.
- 이동된 4개 파일의 제목(`데이터 모델링에서 JOIN까지`, `SQL 작성 순서`, `SQL 논리적 실행 순서`, `Oracle과 SQL Server 차이`)을 참조하는 다른 파일은 이 4개 파일 자기들끼리의 상호 참조(SQL 작성 순서 ↔ SQL 논리적 실행 순서) 1쌍뿐이며, 전체 vault 어디에도 `Hubs/`를 포함한 경로 기반 링크(`[[Hubs/...]]`)가 없었으므로 폴더 이동으로 깨지는 링크가 없다.
- Question·Proposition 파일은 이 4개 축 제목을 참조하지 않는다(수정 대상에서도 제외).

## 8. 예상하지 않은 diff

없음. 이번 단계에서 실제로 변경된 파일은 이동된 4개뿐이며(각각 위치 변경 + frontmatter 6줄 교체), 그 외 54개 atomic Concept, Question, Proposition, 기존 `_reports/*` 파일은 전혀 건드리지 않았다. `Hubs/` 폴더는 빈 채로 남아 있으며 삭제하지 않았다.

## 9. git status --short

이 vault(`OneDrive/문서/Obsidian Vault/`)는 홈 디렉터리 git 저장소(`C:\Users\yjl59`, 브랜치 `portone-push`) 내에서 최초부터 전체가 미추적(`??`) 상태였다(이번 세션 시작 전부터 커밋된 이력이 없음). 따라서 파일 단위 diff가 아니라 폴더 전체가 아래처럼 잡힌다.

```
?? "OneDrive/문서/Obsidian Vault/"
```

git add·commit·push는 지시대로 수행하지 않았다.
