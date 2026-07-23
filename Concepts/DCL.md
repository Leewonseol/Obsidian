---
type: concept
pilot: true
origin:
  - mock-01
learning_tier: 2
unique_question_count: 3
unique_proposition_count: 12
concept_degree: 0
bridge_role: low
direct_question_count: 3
supporting_question_count: 0
study_status: unverified
---

# DCL

## 한 줄 정의

데이터베이스 사용자의 권한을 제어하는 명령어군(GRANT, REVOKE)이다. 원본 마인드맵에는 없어 PDF 해설로 보강되었다.

## 핵심 규칙

- GRANT: 사용자에게 권한을 부여
- REVOKE: 사용자의 권한을 회수
- WITH GRANT OPTION으로 부여된 권한은, Oracle에서 REVOKE 시 하위로 전이된 권한까지 연쇄적으로 회수된다.

## 판단 순서

1. 권한이 누구에게서 누구에게 전이되었는지 경로를 그린다.
2. WITH GRANT OPTION이 붙어 있었는지 확인한다.
3. REVOKE가 발생한 지점을 찾고, 그 이후 연쇄가 어디까지 미치는지 추적한다.

## 자주 혼동하는 개념

| 비교 대상      | 차이                                                |
| ---------- | ------------------------------------------------- |
| DCL vs TCL | DCL은 권한(GRANT/REVOKE), TCL은 트랜잭션(COMMIT/ROLLBACK) |
| DCL vs DDL | DCL은 권한, DDL은 객체 구조                               |

## 대표 함정

- COMMIT(TCL)이나 CREATE(DDL)를 DCL로 착각(M01-Q17).
- WITH GRANT OPTION 연쇄 회수를 특정 권한(SELECT)만 남기거나 일부 사용자만 영향받는다고 오판(M01-Q44, M01-Q45).

## 연결된 문제

- [[M01-Q17]]
- [[M01-Q44]]
- [[M01-Q45]]

## 능동 회상

### 1. DCL에 속하는 대표 명령어 2가지는?

> [!success]- 답 확인
> GRANT, REVOKE.

### 2. WITH GRANT OPTION으로 전이된 권한을 REVOKE하면 어떻게 되는가?

> [!success]- 답 확인
> 하위로 전이된 권한까지 연쇄적으로 모두 회수된다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- DCL은 [[DML]]·[[DDL]]·[[TCL]]과 함께 SQL 명령어의 주요 분류 중 하나다.
- [[TCL]]은 [[Transaction]]을 제어하는 명령어 분류다.

## Source

- 원본에 없음(mock-01 해설 근거) — 보강 필요
