"""Structural curation decisions.

All entries are keyed by the exact concept name in `16_KG_Nodes` (concept names are unique among
concepts; collisions only exist with CLUSTER names, which the build resolves by Node ID).
"""

# ---------------------------------------------------------------------------
# 1. Explicit prerequisite candidates from 17_KG_Edges
# ---------------------------------------------------------------------------
# Only these relation types may become Learning DAG edges.
DAG_CANDIDATE_RELATIONS = ("REQUIRES", "PRECEDES", "ENABLES", "EXPLAINS")

# Relations that must never become directed DAG edges (they become metadata / cards).
FORBIDDEN_DAG_RELATIONS = (
    "CONTRASTS", "AFFECTS", "DIALECT", "DIALECT_OF", "DIALECT_EQUIVALENT",
    "EXCEPTION", "RELATED_TO", "IS_A", "IMPLEMENTS",
)

# Review result for explicit candidates. Anything not listed here is accepted as-is.
# A candidate is never silently dropped: rejected ones are re-classified as metadata and
# reported in cycle_report.json / validation_report.json with the reason below.
EXPLICIT_EDGE_REVIEW = {
    ("HAVING", "SELECT", "PRECEDES"): {
        "decision": "reclassify_as_execution_order",
        "reason": (
            "원본 근거가 '논리적 실행 순서'(FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY)이다. "
            "이는 평가 순서이지 학습 선수관계가 아니다. 학습상으로는 SELECT를 먼저 알아야 "
            "WHERE·GROUP BY·HAVING을 배울 수 있으므로, 이 edge를 DAG에 넣으면 "
            "SELECT→WHERE→GROUP BY→HAVING→SELECT cycle이 생긴다. "
            "'SQL 논리 실행 순서' 노드의 execution_order 규칙 metadata로 이동한다."
        ),
    },
}

# ---------------------------------------------------------------------------
# 2. Placement overrides (cluster re-assignment)
# ---------------------------------------------------------------------------
# The source places a few concepts in a cluster/stage that comes *before* their obvious
# prerequisites, which would force prerequisite edges to run backwards across stages.
# name -> (new cluster code, reason)
PLACEMENT_OVERRIDES = {
    "개체 무결성": ("DM7", "PK(Stage 1 식별자·키)를 알아야 이해되는 무결성 규칙. 원본은 DM0(Stage 0)에 있으나 사용자 Stage 1 정의(개체/참조 무결성)와 같은 DM7로 이동"),
    "참조 무결성": ("DM7", "FK를 전제로 하는 무결성 규칙. DM0(Stage 0) → DM7(Stage 1)"),
    "CHECK": ("MG3", "CHECK는 DDL 제약조건이며 SELECT 조회 문맥(SQ1)과 무관"),
    "UNIQUE": ("MG3", "UNIQUE는 DDL 제약조건. SQ1(Stage 2) → MG3(Stage 7)"),
    "UNIQUE 키워드": ("MG3", "원본 상위 Concept가 UNIQUE이므로 UNIQUE와 같은 Cluster로 이동"),
    "제약조건": ("MG3", "제약조건 상위 개념은 '제약조건·참조동작' Cluster(MG3)에 속함"),
    "NOT NULL": ("MG3", "NOT NULL 제약조건(IS NOT NULL 조건과 별개). CTAS 상속 규칙과 함께 출제되므로 MG3로 이동"),
    "DEFAULT": ("MG2", "DEFAULT는 CREATE/ALTER TABLE의 컬럼 정의. 원본 상위 Concept도 DDL"),
    "DEFAULT 변경": ("MG2", "ALTER TABLE로 DEFAULT를 바꾸는 DDL"),
    "객체명 규칙": ("MG2", "테이블/컬럼 객체 이름 규칙은 CREATE TABLE(DDL) 문맥. 원본 상위 Concept도 DDL"),
    "CTAS": ("MG2", "CREATE TABLE ... AS SELECT는 DDL. SELECT와 CREATE TABLE을 모두 알아야 함"),
    "자료형 변경": ("MG2", "ALTER TABLE MODIFY/ALTER COLUMN으로 자료형을 바꾸는 DDL. 원본 상위 Concept가 ALTER"),
    "날짜 ROUND": ("FN3", "ROUND(숫자 함수)와 DATE를 모두 알아야 하는 날짜 함수. SQ1 → FN3"),
    "날짜 TRUNC": ("FN3", "TRUNC(숫자 함수)와 DATE를 모두 알아야 하는 날짜 함수. SQ1 → FN3"),
    "문자형 MIN/MAX": ("AG1", "집계 함수(MIN/MAX)를 문자형에 적용하는 규칙. 원본 상위 Concept가 집계 함수"),
    "GROUP BY NULL": ("AG1", "GROUP BY가 NULL을 하나의 그룹으로 묶는 규칙. GROUP BY(Stage 5)를 먼저 알아야 함"),
    "IN": ("SQ4", "IN은 WHERE 조건 연산자. IN·NOT IN, NOT IN과 같은 Cluster로 이동"),
    "ORDER BY CASE": ("FN4", "CASE 식을 알아야 이해되는 정렬 기법. SQ5(Stage 2) → FN4(Stage 3)"),
    "그룹 내 비율 함수": ("AG3", "RATIO_TO_REPORT·PERCENT_RANK·CUME_DIST·NTILE 묶음은 윈도우 함수 분류"),
    "Oracle DDL 자동 커밋": ("MG5", "COMMIT/Transaction(Stage 8)을 알아야 이해되는 동작"),
    "SQL Server 트랜잭션": ("MG5", "Transaction(Stage 8) 개념의 SQL Server 동작"),
}

# Primary parent overrides when the source gives multiple BELONGS_TO parents or none fits.
PRIMARY_PARENT_OVERRIDES = {
    # name -> (parent concept name or None to hang directly under the cluster, reason)
    "정규표현식": (None, "원본 BELONGS_TO가 '정규표현식 ↔ 정규표현식 함수'로 서로를 부모로 가리키는 2-cycle. "
                    "패턴 언어(정규표현식)를 상위로, 함수군을 하위로 정리"),
    "정규표현식 함수": ("정규표현식", "위 2-cycle 해소: REGEXP_* 함수군은 정규표현식 패턴을 인자로 받음"),
}

# ---------------------------------------------------------------------------
# 3. Synthetic nodes (curated, not in the source sheet)
# ---------------------------------------------------------------------------
# kind = "structure": a learning waypoint that the user's own examples require
#                     (e.g. 윈도우 함수 → OVER → 순위 함수 → RANK).
# kind = "integration": Stage 9 review nodes that integrate dialect differences / exam traps.
#                       Grounded in 04_Mindmap_Gaps gap families.
SYNTHETIC_NODES = [
    {
        "id": "X001", "name": "순환 관계(자기참조)", "node_type": "CONCEPT", "cluster": "DM4",
        "kind": "structure",
        "basis": "사용자 예시 경로 'JOIN/관계 개념 → 부모-자식/self-referencing 구조 → 계층형 질의'. "
                 "데이터 모델링의 순환(재귀) 관계에 해당하며 셀프 조인·계층형 질의의 공통 선수 구조.",
    },
    {
        "id": "X002", "name": "OVER 절", "node_type": "SYNTAX", "cluster": "AG3",
        "kind": "structure",
        "basis": "사용자 예시 경로 '윈도우 함수 → OVER → PARTITION BY / ORDER BY → 순위 함수'. "
                 "04_Mindmap_Gaps '윈도우 함수: OVER/PARTITION/ORDER/프레임으로 분해'.",
    },
    {
        "id": "X003", "name": "순위 함수", "node_type": "FUNCTION", "cluster": "AG3",
        "kind": "structure",
        "basis": "SQL 전문가 가이드의 '그룹 내 순위 함수' 분류(RANK·DENSE_RANK·ROW_NUMBER). "
                 "17_KG_Edges의 IS_A reason '순위 함수'.",
    },
    {
        "id": "X004", "name": "행 순서 함수", "node_type": "FUNCTION", "cluster": "AG3",
        "kind": "structure",
        "basis": "SQL 전문가 가이드의 '그룹 내 행 순서 함수' 분류(FIRST_VALUE·LAST_VALUE·LAG·LEAD). "
                 "17_KG_Edges의 IS_A reason '행 위치/값 탐색 함수'.",
    },
    # ---- Stage 9 / XC1 : DBMS 방언 ----
    {
        "id": "X101", "name": "NULL 처리 DBMS 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "NULL의 집합·그룹 동작",
        "basis": "사용자 Stage 9 정의 'NULL 차이'. 20_Hubs_Rules NULL 허브의 DIALECT 관계(빈 문자열과 NULL(Oracle)).",
    },
    {
        "id": "X102", "name": "NULL 정렬 DBMS 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "NULL 정렬 DBMS 차이",
        "basis": "04_Mindmap_Gaps gap family 'NULL 정렬 DBMS 차이'(현행). 사용자 Stage 9 정의 'NULL 정렬 차이'.",
    },
    {
        "id": "X103", "name": "Top-N 문법 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "Top-N DBMS 방언",
        "basis": "04_Mindmap_Gaps gap family 'Top-N DBMS 방언'(현행). DIALECT_OF: Oracle→ROWNUM, SQL Server→TOP, ANSI→FETCH FIRST.",
    },
    {
        "id": "X104", "name": "차집합 MINUS/EXCEPT 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "집합 연산자",
        "basis": "17_KG_Edges MINUS DIALECT_EQUIVALENT EXCEPT. 사용자 Stage 9 정의 'MINUS / EXCEPT'.",
    },
    {
        "id": "X105", "name": "DDL 커밋 동작 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "Transaction",
        "basis": "17_KG_Edges DDL DIALECT Oracle DDL 자동 커밋. 사용자 Stage 9 정의 'DDL commit 차이'.",
    },
    {
        "id": "X106", "name": "문자열 함수 DBMS 차이", "node_type": "RULE", "cluster": "XC1",
        "kind": "integration", "gap_family": "문자열 함수 DBMS 차이",
        "basis": "04_Mindmap_Gaps gap family '문자열 함수 DBMS 차이'(현행/공통).",
    },
    # ---- Stage 9 / XC2 : 실행순서·시험 함정 ----
    {
        "id": "X201", "name": "별칭 가시성 종합", "node_type": "RULE", "cluster": "XC2",
        "kind": "integration", "gap_family": "별칭 가시성",
        "basis": "04_Mindmap_Gaps gap family '별칭 가시성'(현행). 20_Hubs_Rules 'SQL 논리 실행 순서' 허브.",
    },
    {
        "id": "X202", "name": "NULL 함정 종합", "node_type": "RULE", "cluster": "XC2",
        "kind": "integration", "gap_family": "NULL 3값 논리 확장",
        "basis": "04_Mindmap_Gaps gap family 'NULL 3값 논리 확장', '집계식의 NULL 위치', '공집합·집계 반환값'. 20_Hubs_Rules NULL 허브.",
    },
    {
        "id": "X203", "name": "OUTER JOIN 필터 위치 종합", "node_type": "RULE", "cluster": "XC2",
        "kind": "integration", "gap_family": "OUTER JOIN 필터 위치",
        "basis": "04_Mindmap_Gaps gap family 'OUTER JOIN 필터 위치', 'OUTER JOIN 보존 규칙'(현행). 20_Hubs_Rules JOIN 허브.",
    },
]

# Synthetic nodes' hierarchy parents (name of concept; None = directly under cluster)
SYNTHETIC_PARENTS = {
    "순환 관계(자기참조)": "관계",
    "OVER 절": "윈도우 함수",
    "순위 함수": "윈도우 함수",
    "행 순서 함수": "윈도우 함수",
}

# After synthetic group nodes exist, these concepts hang under them in the hierarchy
# (display grouping only; prerequisite edges are defined separately in prerequisites.py).
HIERARCHY_REPARENT = {
    "RANK": "순위 함수",
    "DENSE_RANK": "순위 함수",
    "ROW_NUMBER": "순위 함수",
    "LAG": "행 순서 함수",
    "LEAD": "행 순서 함수",
    "FIRST_VALUE": "행 순서 함수",
    "LAST_VALUE": "행 순서 함수",
    "PARTITION BY": "OVER 절",
    "ROWS/RANGE 프레임": "OVER 절",
    "RATIO_TO_REPORT": "그룹 내 비율 함수",
    "PERCENT_RANK": "그룹 내 비율 함수",
    "CUME_DIST": "그룹 내 비율 함수",
    "NTILE": "그룹 내 비율 함수",
}

# Legacy pseudo-stage for D7 clusters (LG1–LG5), kept after Stage 9 as optional study.
LEGACY_STAGE = {
    "stage": "L", "order": 10, "title": "구범위·레거시 (선택)",
    "goal": "52회 이후 현행 출제 증거가 없는 과거 범위(성능·옵티마이저·분산 DB·PL/SQL·물리 조인·성능 모델링)",
    "prereq_stages": [9],
}

# Display tier overrides (core = shown in the initial collapsed view).
FORCE_CORE = {
    "SELECT", "WHERE", "ORDER BY", "NULL", "SQL 논리 실행 순서", "자료형", "JOIN", "서브쿼리",
    "집합 연산자", "집계 함수", "GROUP BY", "HAVING", "윈도우 함수", "Top-N", "PIVOT·UNPIVOT",
    "계층형 질의", "DML", "DDL", "제약조건", "VIEW", "Transaction", "TCL", "DCL",
    "엔터티", "속성", "관계", "ERD", "식별자", "정규화", "3단계 스키마", "데이터 모델링 3단계",
    "단일행 함수", "정규표현식", "CASE", "OUTER JOIN", "INNER JOIN", "WITH 절",
    "ANSI/ISO SQL", "Oracle SQL", "SQL Server",
}
FORCE_DETAIL = set()
