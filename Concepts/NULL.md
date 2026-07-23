---
type: concept
pilot: true
origin:
  - current-map
learning_tier: 1
unique_question_count: 16
unique_proposition_count: 47
concept_degree: 9
bridge_role: high
direct_question_count: 9
supporting_question_count: 7
study_status: unverified
axis_membership:
  - modeling_to_join
  - sql_writing_order
  - sql_execution_order
  - oracle_sqlserver
axis_confidence: medium
axis_review_required: false
---

# NULL

## 한 줄 정의

값이 존재하지 않는 상태이며, 비교·연산·집계·정렬에서 일반 값과 다른 규칙이 적용된다.

## 핵심 규칙

- [[PK]] 컬럼은 NULL을 저장할 수 없다(존재성).
- = 또는 != 같은 일반 비교 연산자로는 NULL을 비교할 수 없다. IS NULL / IS NOT NULL만 가능하다.
- 산술 연산(값+NULL)의 결과는 NULL이지만, [[집계 함수]]는 일반적으로 NULL을 제외하고 계산한다.
- [[COUNT]](*)는 컬럼 값이 아니라 행 자체를 세므로 NULL 여부와 관계없이 모든 행을 센다.
- AVG는 NULL을 분자와 분모 모두에서 제외한다.
- NOT IN 목록에 NULL이 하나라도 포함되면 전체 비교가 UNKNOWN이 되어 결과 집합이 비어버릴 수 있다.
- [[OUTER JOIN]]에서 매칭되지 않는 반대편 열은 NULL로 채워진다.
- 정렬([[ORDER BY]]) 시 NULL의 위치는 Oracle과 SQL Server가 서로 다르다.

## 판단 순서

1. NULL이 어느 위치(연산/비교/집계/조인/정렬)에 등장하는지 먼저 식별한다.
2. 그 위치에 적용되는 NULL 규칙이 "포함"인지 "제외"인지 확인한다(예: COUNT(*)=포함, COUNT(열)=제외).
3. 여러 함수·연산이 중첩된 경우 안쪽부터 순서대로 NULL 처리 결과를 계산한다.
4. DBMS 차이(정렬 위치 등)가 관련되어 있는지 마지막으로 확인한다.

## 자주 혼동하는 개념

| 비교 대상                   | 차이                                                     |
| ----------------------- | ------------------------------------------------------ |
| COUNT(*) vs COUNT(열)    | COUNT(*)는 NULL 포함, COUNT(열)은 NULL 제외                   |
| IN vs NOT IN            | IN은 NULL이 목록에 있어도 영향 없음, NOT IN은 NULL이 있으면 전체가 UNKNOWN |
| NULL 산술연산 vs NULL 집계    | 산술연산은 NULL 전파(결과 NULL), 집계 함수는 대부분 NULL 무시             |
| Oracle vs SQL Server 정렬 | Oracle ASC는 NULL이 마지막, SQL Server ASC는 NULL이 처음        |

## 대표 함정

- SUM에 NULL이 있으면 결과 전체가 NULL이 된다고 착각(M01-Q11, M01-Q38).
- NOT IN(서브쿼리/목록)에 NULL이 섞여 있는데 이를 인지하지 못해 예상과 다른 빈 결과를 얻음(M01-Q22).
- AVG가 NULL을 "0"으로 바꿔 계산한다거나, 분모(행 수)에 NULL을 포함한다고 착각(M01-Q29).
- OUTER JOIN으로 생긴 NULL을 COUNT(*)와 COUNT(열)에 각각 다르게 적용하지 못함(M01-Q19).

## 연결된 문제

- [[M01-Q01]]
- [[M01-Q07]]
- [[M01-Q09]]
- [[M01-Q11]]
- [[M01-Q13]]
- [[M01-Q14]]
- [[M01-Q19]]
- [[M01-Q20]]
- [[M01-Q22]]
- [[M01-Q26]]
- [[M01-Q27]]
- [[M01-Q29]]
- [[M01-Q32]]
- [[M01-Q37]]
- [[M01-Q38]]
- [[M01-Q49]]

## 능동 회상

### 1. COUNT(*)와 COUNT(열)은 NULL을 각각 어떻게 처리하는가?

> [!success]- 답 확인
> COUNT(*)는 NULL을 포함해 모든 행을 세고, COUNT(열)은 해당 열이 NULL인 행을 제외한다.

### 2. WHERE COL = NULL이 항상 아무 행도 반환하지 않는 이유는?

> [!success]- 답 확인
> NULL은 일반 비교 연산자(=)로 비교할 수 없어 항상 UNKNOWN이 되기 때문이다.

### 3. NOT IN 목록에 NULL이 포함되면 전체 결과가 어떻게 되는가?

> [!success]- 답 확인
> NULL과의 비교가 UNKNOWN이 되어 전체 조건이 참이 될 수 없으므로 결과 집합이 비어버린다.

### 4. LEFT OUTER JOIN에서 매칭되지 않은 반대편 열은 어떤 값이 되는가?

> [!success]- 답 확인
> NULL로 채워진다.

### 5. Oracle과 SQL Server에서 ORDER BY 시 NULL 위치가 어떻게 다른가?

> [!success]- 답 확인
> Oracle의 ASC는 NULL이 마지막, SQL Server의 ASC는 NULL이 처음에 온다.

## 연결망 학습 경로

1. 능동 회상 질문에 먼저 답한다.
2. 접힌 답을 열어 비교한다.
3. 연결된 Question Node를 푼다.
4. 헷갈린 선지만 Proposition Node에서 확인한다.
5. Local Graph에서 다음 개념으로 이동한다.

- [[SQLD 학습 대시보드]]

## 관련 개념

- [[PK]]는 NULL을 허용하지 않지만 [[제약조건]] 중 UNIQUE는 NULL을 허용한다는 점에서 다르다.
- [[집계 함수]]는 대부분 NULL을 제외하고 계산하지만 COUNT(*)만 예외적으로 NULL을 포함한다.
- [[OUTER JOIN]]은 불일치하는 행에 NULL을 채워 넣어 이후 [[집계 함수]] 결과에 영향을 준다.
- [[개체 무결성]]은 PK의 NULL 금지 규칙에서 출발한다.

## Source

- 데이터 모델링.md — 9. 식별자(주식별자 특징: 존재성(NULL 불가))
- SQL 관리 구문.md — 3. DDL 제약조건(PRIMARY KEY: NULL X)
- SQL 기본.md — 6. WHERE절(NULL 조건), 2. SELECT절(산술 연산에 NULL 포함 시 결과도 NULL)
