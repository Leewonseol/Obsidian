"""Curated inferred prerequisite edges.

Direction is always   prerequisite  ->  next concept
("to understand <next>, you must already know <prerequisite>").

Rules followed when writing this list (see README):
- only obvious learning prerequisites; never similarity, never "appeared in the same exam"
- every edge carries a human-written reason ({src}/{dst} are filled in by the build)
- CONTRASTS / DIALECT / AFFECTS / IS_A pairs are NOT copied automatically. When a curated edge
  happens to cover a pair that also has such a relation in the source, the build records it in
  `related_source_relations` for transparency, but the reason must stand on its own.
"""

EDGES = []  # (prerequisite, next, reason)


def req(src, dsts, reason):
    """src is a prerequisite of every name in dsts."""
    if isinstance(dsts, str):
        dsts = [dsts]
    for dst in dsts:
        EDGES.append((src, dst, reason))


def needs(dst, srcs, reason):
    """dst needs every name in srcs first."""
    if isinstance(srcs, str):
        srcs = [srcs]
    for src in srcs:
        EDGES.append((src, dst, reason))


def chain(names, reason):
    for a, b in zip(names, names[1:]):
        EDGES.append((a, b, reason))


# =============================================================================
# Stage 0 · 모델링 기초
# =============================================================================
# DM0 데이터 모델링 원리
req("데이터 모델링 정의", ["데이터 모델링 특징", "데이터 모델링 관점", "데이터 모델링 3단계",
                     "데이터 모델링 3대 유의점", "업무 규칙", "데이터 모델링 재사용성"],
    "{dst}은(는) 데이터 모델링이 무엇인지(현실 업무를 데이터 구조로 추상화) 알아야 이해할 수 있음")
req("데이터 모델링 특징", ["추상화", "단순화", "명확화", "완전성", "중복 배제"],
    "{dst}은(는) '데이터 모델링 특징' 목록의 한 항목이므로 특징 전체 맥락을 먼저 학습")
req("데이터 모델링 관점", "데이터 관점",
    "데이터 관점은 데이터/프로세스/상관 관점 중 하나이므로 관점 분류를 먼저 알아야 함")
req("데이터 모델링 3단계", "개념적 데이터 모델링",
    "개념적 모델링은 3단계(개념→논리→물리) 중 첫 단계")
chain(["개념적 데이터 모델링", "논리적 데이터 모델링", "물리적 데이터 모델링"],
      "모델링 단계는 개념→논리→물리 순으로 구체화되며 이전 단계의 산출물을 입력으로 받음")
req("데이터 모델링 3대 유의점", ["중복", "비유연성", "비일관성"],
    "{dst}은(는) 데이터 모델링 3대 유의점(중복·비유연성·비일관성)의 한 항목")
req("물리적 데이터 모델링", "데이터 용량",
    "데이터 용량 산정은 물리적 데이터 모델링 단계의 고려사항")
req("엔터티", "슈퍼타입/서브타입",
    "슈퍼타입/서브타입은 엔터티를 공통/개별 속성으로 나누는 구조이므로 엔터티 개념 선행")

# DM1 스키마·독립성
req("3단계 스키마", ["외부 스키마", "개념 스키마", "내부 스키마"],
    "{dst}은(는) ANSI/SPARC 3단계 스키마 구조의 한 계층")
needs("데이터 독립성", ["외부 스키마", "개념 스키마", "내부 스키마"],
      "논리적 독립성(외부↔개념)과 물리적 독립성(개념↔내부)은 각 스키마 사이의 매핑으로 정의되므로 {src}을(를) 알아야 함")

# DM2 엔터티
req("엔터티", ["인스턴스", "엔터티 특징", "엔터티 분류", "엔터티 명명 규칙", "엔터티 도출"],
    "{dst}은(는) 엔터티 개념을 전제로 함")
req("엔터티 분류", "엔터티 발생시점 분류",
    "발생시점 분류(기본/중심/행위)는 엔터티 분류 기준 중 하나")
req("엔터티 발생시점 분류", "기본 엔터티",
    "기본 엔터티는 발생시점 분류의 첫 유형")
chain(["기본 엔터티", "중심 엔터티", "행위 엔터티"],
      "중심 엔터티는 기본 엔터티로부터, 행위 엔터티는 두 개 이상의 부모(기본/중심) 엔터티로부터 발생하므로 앞 유형을 먼저 알아야 구분 가능")
needs("엔터티/인스턴스/속성 관계", ["인스턴스", "속성"],
      "엔터티·인스턴스·속성의 관계를 판단하려면 {src} 개념이 먼저 필요")
needs("엔터티/속성/인스턴스 구분", ["인스턴스", "속성"],
      "엔터티·속성·인스턴스를 구분하려면 {src} 개념이 먼저 필요")
req("관계 차수", "M:N 해소",
    "M:N 해소는 관계 차수 중 M:N을 이해해야 필요성이 보임")
req("M:N 해소", "관계 엔터티",
    "관계 엔터티는 M:N 관계를 1:M + M:1로 분해(해소)한 결과물")
req("관계 엔터티", "교차 엔터티",
    "교차 엔터티는 관계 엔터티의 다른 이름/형태")

# DM3 속성·도메인
req("엔터티", "속성", "속성은 엔터티가 가지는 성질(정보 항목)")
req("속성", ["속성 특징", "속성값", "속성 명명", "도메인", "속성 분류"],
    "{dst}은(는) 속성 개념을 전제로 함")
req("속성 분류", ["기본 속성", "설계 속성", "파생 속성", "일반 속성", "단일값 속성", "다중값 속성", "복합 속성"],
    "{dst}은(는) 속성 분류 체계(특성별·구성방식별·값 개수별)의 한 유형")

# DM4 관계·ERD
req("엔터티", "관계", "관계는 엔터티(인스턴스) 사이의 연관이므로 엔터티 선행")
req("관계", ["관계명", "관계 차수", "관계 선택성", "상호배타 관계", "ERD", "순환 관계(자기참조)"],
    "{dst}은(는) 관계 개념을 전제로 함")
req("관계 선택성", ["선택 참여", "필수 참여", "ERD 선택성"],
    "{dst}은(는) 관계 선택성(필수/선택 참여)의 세부 내용")
req("ERD", "ERD 표기법", "표기법은 ERD를 그리는 방법이므로 ERD 개념 선행")
req("ERD 표기법", ["IE 표기법", "Barker 표기법", "Peter Chen 표기법", "IDEFIX 표기법", "UML 표기법", "ERD 선택성"],
    "{dst}은(는) ERD 표기법의 한 종류/요소")
req("논리적 데이터 모델링", "관계형 모델",
    "관계형 모델(테이블·행·열)은 논리적 데이터 모델링 단계에서 사용하는 표현 모델")

# =============================================================================
# Stage 1 · 키·정규화·무결성
# =============================================================================
# DM5 식별자·키
req("엔터티", "식별자", "식별자는 엔터티의 인스턴스를 유일하게 구분하는 속성")
req("식별자", ["식별자 특징", "식별자 명명 규칙", "주식별자", "보조 식별자", "내부 식별자", "외부 식별자",
             "단일 식별자", "복합 식별자", "본질 식별자", "인조 식별자", "후보키"],
    "{dst}은(는) 식별자 개념과 분류 체계를 전제로 함")
req("주식별자", "주식별자 특징", "주식별자의 특징(유일성·최소성·불변성·존재성)은 주식별자 개념 선행")
req("주식별자 특징", ["주식별자 유일성", "주식별자 최소성", "주식별자 불변성", "주식별자 존재성"],
    "{dst}은(는) 주식별자 4대 특징 중 하나")
req("주식별자 특징", "주식별자 도출", "주식별자는 4대 특징을 만족하는 속성으로 도출")
req("주식별자 도출", ["주식별자 선정", "주식별자 선택"],
    "{dst}은(는) 주식별자 도출 기준을 적용하는 과정")
req("복합 식별자", "복합키", "복합키는 복합 식별자를 물리 테이블 키로 구현한 것")
req("인조 식별자", "대리키", "대리키는 인조 식별자의 물리적 구현")
req("후보키", "PK", "PK(기본키)는 후보키 중에서 선택한 키")
req("주식별자", "PK", "논리 모델의 주식별자가 물리 테이블의 PK로 구현됨")
req("PK", "FK", "FK는 부모 테이블의 PK(또는 UNIQUE 키)를 참조")
req("관계", "FK", "FK는 엔터티 간 관계를 테이블에 구현하는 수단")
req("외부 식별자", "FK", "외부 식별자(다른 엔터티에서 온 식별자)가 물리적으로 FK가 됨")
needs("식별 관계", ["관계", "외부 식별자", "주식별자"],
      "식별 관계는 부모의 식별자가 자식의 주식별자에 포함되는 관계이므로 {src}을(를) 알아야 판별 가능")
needs("비식별 관계", ["관계", "외부 식별자"],
      "비식별 관계는 부모 식별자가 자식의 일반 속성(FK)으로만 전이되는 관계이므로 {src}을(를) 알아야 판별 가능")
req("식별 관계", ["주식별자 상속", "동일 생명주기"],
    "{dst}은(는) 식별 관계의 성질(부모 키 상속 / 부모와 생명주기 공유)")

# DM6 정규화·반정규화
req("중복", "이상현상", "삽입·갱신·삭제 이상은 데이터 중복에서 발생")
req("이상현상", "정규화", "정규화는 이상현상을 제거하기 위한 절차")
req("정규화", ["1NF", "함수적 종속", "반정규화"],
    "{dst}은(는) 정규화의 목적과 절차를 먼저 알아야 이해 가능")
req("다중값 속성", "1NF", "1NF는 다중값(반복) 속성을 원자값으로 분리하는 단계")
req("함수적 종속", ["부분 함수 종속", "이행 함수 종속"],
    "{dst}은(는) 함수적 종속(결정자→종속자)의 특수한 형태")
req("PK", "부분 함수 종속", "부분 함수 종속은 복합 PK의 '일부'에만 종속되는 것이므로 PK 개념 필요")
req("1NF", "2NF", "2NF는 1NF를 만족한 릴레이션에 적용")
req("부분 함수 종속", "2NF", "부분 함수 종속 개념을 알아야 2NF를 판별할 수 있음")
req("2NF", "3NF", "3NF는 2NF를 만족한 릴레이션에 적용")
req("이행 함수 종속", "3NF", "이행 함수 종속 개념을 알아야 3NF를 판별할 수 있음")
req("3NF", "BCNF", "BCNF는 3NF를 강화한 정규형")
req("후보키", "BCNF", "BCNF는 '모든 결정자가 후보키'라는 조건이므로 후보키 개념 필요")
req("반정규화", ["관계 반정규화", "컬럼 반정규화", "컬럼 중복", "수직 분할", "무결성 저하"],
    "{dst}은(는) 반정규화 기법/부작용의 하나")

# DM7 무결성
req("PK", "개체 무결성", "개체 무결성(PK는 NULL·중복 불가)은 PK가 보장하는 규칙")
req("FK", "참조 무결성", "참조 무결성은 FK 값이 부모 PK에 존재(또는 NULL)해야 한다는 규칙")
req("참조 무결성", "ON DELETE CASCADE", "ON DELETE CASCADE는 부모 삭제 시 참조 무결성을 유지하는 참조 동작")
req("도메인", "도메인 무결성", "도메인 무결성은 속성 값이 정의된 도메인 안에 있어야 한다는 규칙")

# =============================================================================
# Stage 2 · SQL 실행 모델
# =============================================================================
# SQ0
req("관계형 모델", "SQL의 특징", "SQL은 관계형 모델(테이블)을 다루는 집합 기반 언어이므로 관계형 모델 선행")
req("SQL의 특징", ["SQL 비절차성", "SQL 선언적 언어", "SQL 집합적 언어"],
    "{dst}은(는) SQL 언어 특징의 한 항목")
req("SELECT", "SQL 논리 실행 순서", "SELECT 문장의 각 절을 알아야 그 평가 순서를 이해할 수 있음")

# SQ1 SELECT·FROM·별칭
req("SELECT", ["ALIAS", "테이블 별칭", "DISTINCT"], "{dst}은(는) SELECT 문장의 구성 요소")
req("ALIAS", "컬럼 별칭 대소문자", "컬럼 별칭의 대소문자 규칙은 별칭(ALIAS) 개념 선행")
needs("문자 비교", ["CHAR", "VARCHAR"],
      "문자 비교 규칙(공백 패딩 비교 vs 비패딩 비교)은 {src} 자료형의 저장 방식을 알아야 이해 가능")
req("SELECT", "SELECT INTO", "SELECT INTO는 SELECT 결과를 변수/새 테이블에 넣는 변형 문법")

# SQ2 자료형·리터럴·형변환
req("자료형", ["CHAR", "VARCHAR", "NUMERIC", "DATE", "암시적 형변환", "명시적 형변환", "문자 리터럴 따옴표 이스케이프"],
    "{dst}은(는) 자료형 개념을 전제로 함")
req("CHAR", "CHAR 후행 공백", "CHAR는 고정 길이라 남는 자리를 공백으로 채우므로 CHAR 개념 선행")

# SQ3 NULL·3값 논리
req("NULL", ["NULL 비교", "IS NULL", "NULL 산술 연산", "빈 문자열과 NULL(Oracle)", "DISTINCT NULL",
             "NULL 정렬", "NOT NULL", "NVL", "NVL2", "COALESCE", "NULLIF", "NULL 집계", "COUNT(열)",
             "GROUP BY NULL", "OUTER JOIN", "계층 전개 NULL 종료"],
    "{dst}은(는) NULL이 '값이 없음/알 수 없음' 상태라는 것을 알아야 이해 가능")
req("WHERE", "NULL 비교", "NULL 비교는 WHERE 조건식에서 발생하는 문제")
req("NULL 비교", ["UNKNOWN", "IS NULL"],
    "NULL과의 비교 결과가 TRUE/FALSE가 아닌 UNKNOWN이 됨을 알아야 {dst}을(를) 이해 가능")
req("IS NULL", "IS NOT NULL", "IS NOT NULL은 IS NULL의 부정형")
req("DISTINCT", "DISTINCT NULL", "DISTINCT가 NULL을 하나로 묶는 규칙은 DISTINCT 개념 선행")
req("UNKNOWN", ["IN + NULL", "NOT IN"],
    "{dst}의 결과는 UNKNOWN(3값 논리)과 WHERE가 TRUE만 통과시키는 규칙으로 설명됨")
req("ORDER BY", "NULL 정렬", "NULL 정렬 위치 규칙은 ORDER BY 개념 선행")
req("NULL 정렬", ["Oracle NULL 정렬", "SQL Server NULL 정렬", "NULLS FIRST", "NULLS LAST"],
    "{dst}은(는) NULL 정렬 규칙의 DBMS별 동작/제어 문법")

# SQ4 WHERE·조건·패턴
req("SELECT", "WHERE", "WHERE는 SELECT 문장의 행 필터 절")
req("WHERE", ["AND", "OR", "NOT", "BETWEEN", "IN·NOT IN", "LIKE", "날짜 범위 조회", "연산자 우선순위",
              "SELECT 별칭 WHERE 사용 불가", "공집합"],
    "{dst}은(는) WHERE 조건절의 문맥에서 학습")
needs("AND/OR 우선순위", ["AND", "OR", "NOT"],
      "우선순위(NOT > AND > OR)를 따지려면 {src} 연산자를 먼저 알아야 함")
req("BETWEEN", ["BETWEEN 경계 포함", "날짜 경계", "NON-EQUI JOIN"],
    "{dst}은(는) BETWEEN의 양 끝 포함 범위 비교를 전제로 함")
req("IN·NOT IN", "IN", "IN은 IN·NOT IN 조건 묶음의 기본 형태")
req("IN", ["NOT IN", "행값 IN", "IN + NULL", "다중행 서브쿼리"],
    "{dst}은(는) IN(목록 중 하나와 일치) 연산자를 전제로 함")
req("NOT", "NOT IN", "NOT IN은 IN 조건의 부정(NOT)")
req("LIKE", ["와일드카드", "LIKE 컬럼 패턴", "SQL Server LIKE []", "정규표현식", "REGEXP_LIKE"],
    "{dst}은(는) LIKE 패턴 매칭 개념을 전제로 함")
req("와일드카드", ["LIKE ESCAPE", "SQL Server LIKE []"],
    "{dst}은(는) 와일드카드(%, _)의 의미를 알아야 이해 가능")
req("DATE", "날짜 범위 조회", "DATE가 시·분·초를 포함한다는 것을 알아야 날짜 범위 조건을 정확히 작성 가능")
req("날짜 범위 조회", ["날짜 경계", "날짜 반개방 구간"], "{dst}은(는) 날짜 범위 조회의 경계 처리 규칙")
req("ALIAS", ["SELECT 별칭 WHERE 사용 불가", "ORDER BY 별칭"],
    "{dst} 규칙은 컬럼 별칭(ALIAS)을 알아야 이해 가능")

# SQ5 ORDER BY·정렬
req("ORDER BY", ["ASC", "DESC", "다중 열 ORDER BY", "ORDER BY 순서번호"],
    "{dst}은(는) ORDER BY 정렬 문법의 구성 요소")

# =============================================================================
# Stage 3 · 표현식·함수
# =============================================================================
req("SELECT", "단일행 함수", "단일행 함수는 SELECT/WHERE 절의 각 행에 적용되는 함수")
req("단일행 함수", ["문자형 함수", "숫자형 함수", "CASE"], "{dst}은(는) 단일행 함수의 한 분류")
req("문자형 함수", ["LOWER", "UPPER", "ASCII", "CONCAT", "SUBSTR", "LENGTH", "LEN", "INSTR", "LPAD",
                  "LTRIM", "RTRIM", "TRIM", "REPLACE"],
    "{dst}은(는) 문자형 단일행 함수")
req("LENGTH", "LENGTHB", "LENGTHB는 LENGTH의 바이트 단위 버전")
req("SUBSTR", "SUBSTR 음수 위치", "음수 시작 위치 규칙은 SUBSTR(문자열, 시작, 길이) 동작을 알아야 이해 가능")
req("숫자형 함수", ["ROUND", "TRUNC", "CEIL", "FLOOR", "MOD"], "{dst}은(는) 숫자형 단일행 함수")
req("DATE", ["SYSDATE", "Oracle 날짜 연산", "TO_CHAR", "TO_DATE", "EXTRACT", "DATE_FORMAT", "날짜 ROUND", "날짜 TRUNC"],
    "{dst}은(는) DATE 자료형(날짜+시각)을 다루는 함수/연산")
req("명시적 형변환", ["TO_CHAR", "TO_DATE"], "{dst}은(는) 명시적 형변환 함수")
req("TO_CHAR", "Oracle 날짜 포맷", "날짜 포맷 모델(YYYY, MM, HH24 …)은 TO_CHAR 사용법 선행")
req("TO_DATE", "TO_DATE 기본값", "생략된 날짜 요소의 기본값 규칙은 TO_DATE 동작 선행")
req("ROUND", "날짜 ROUND", "날짜 ROUND는 숫자 ROUND의 반올림 개념을 날짜 단위에 적용")
req("TRUNC", "날짜 TRUNC", "날짜 TRUNC는 숫자 TRUNC의 절삭 개념을 날짜 단위에 적용")
req("CASE", ["DECODE", "ORDER BY CASE"], "{dst}은(는) CASE 조건 분기 개념을 전제로 함")
req("ORDER BY", "ORDER BY CASE", "ORDER BY CASE는 ORDER BY에 CASE 식을 넣는 기법")
req("NVL", "NVL2", "NVL2는 NVL에 'NULL이 아닐 때 값'을 추가한 확장")
req("정규표현식", ["정규식 메타문자", "정규표현식 함수"], "{dst}은(는) 정규표현식 패턴 개념을 전제로 함")
req("정규식 메타문자", ["정규식 *", "정규식 +", "정규식 ?", "정규식 ^", "정규식 $", "정규식 \\w", "정규식 {m,}"],
    "{dst}은(는) 정규식 메타문자의 하나")
req("정규식 메타문자", "정규표현식 함수", "REGEXP_* 함수의 패턴 인자를 해석하려면 메타문자를 알아야 함")
req("정규표현식 함수", ["REGEXP_LIKE", "REGEXP_REPLACE", "REGEXP_SUBSTR", "REGEXP_INSTR", "REGEXP_COUNT"],
    "{dst}은(는) 정규표현식 함수군의 하나")
req("SUBSTR", "REGEXP_SUBSTR", "REGEXP_SUBSTR은 SUBSTR의 '패턴으로 잘라내기' 버전")
req("REPLACE", "REGEXP_REPLACE", "REGEXP_REPLACE는 REPLACE의 '패턴으로 치환' 버전")
req("INSTR", "REGEXP_INSTR", "REGEXP_INSTR은 INSTR의 '패턴 위치 찾기' 버전")

# =============================================================================
# Stage 4 · 관계 결합
# =============================================================================
# JN1 JOIN
req("SELECT", "JOIN", "JOIN은 SELECT의 FROM 절에서 여러 테이블을 결합")
req("FK", "JOIN", "조인 조건은 보통 PK-FK 관계로 작성되므로 FK 개념 선행")
req("JOIN", ["CARTESIAN PRODUCT", "EQUI JOIN", "N-1 조인 조건", "모호한 컬럼", "셀프 조인", "조인 중복 증폭",
             "NON-EQUI JOIN"],
    "{dst}은(는) JOIN의 기본 개념(테이블 결합과 조인 조건)을 전제로 함")
req("WHERE", "EQUI JOIN", "전통적 EQUI JOIN은 WHERE 절의 등호 조건으로 작성")
req("WHERE", "JOIN", "조인 조건은 WHERE(전통 문법) 또는 ON에 쓰는 조건식이므로 WHERE 조건식을 먼저 알아야 함")
req("EQUI JOIN", "INNER JOIN", "INNER JOIN은 조인 조건을 만족하는 행만 남기는 (주로 등가) 조인의 ANSI 표기")
req("CARTESIAN PRODUCT", "CROSS JOIN", "CROSS JOIN은 카티션 곱을 명시적으로 만드는 문법")
req("테이블 별칭", ["모호한 컬럼", "셀프 조인"], "{dst}은(는) 테이블 별칭으로 컬럼 소속을 구분해야 해결/작성 가능")
req("순환 관계(자기참조)", "셀프 조인", "셀프 조인은 한 테이블 안의 자기참조(부모-자식) 관계를 조인으로 펼치는 것")
req("관계 차수", "조인 중복 증폭", "1:M 조인에서 1쪽 행이 M배로 늘어나는 현상은 관계 차수 이해가 선행")
req("INNER JOIN", ["ON", "OUTER JOIN", "복합 FK 조인"], "{dst}은(는) INNER JOIN(매칭 행 결합)을 먼저 알아야 이해 가능")
req("복합 식별자", "복합 FK 조인", "복합 FK 조인은 여러 컬럼으로 된 키를 모두 조인 조건에 걸어야 함")
req("ON", "USING", "USING은 같은 이름 컬럼에 대한 ON 등가 조건의 축약")
req("USING", "NATURAL JOIN", "NATURAL JOIN은 모든 동일 이름 컬럼에 대한 암묵적 USING")
req("OUTER JOIN", ["보존 테이블", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "Oracle (+) OUTER JOIN", "OUTER JOIN 조건 위치"],
    "{dst}은(는) OUTER JOIN(비매칭 행 보존) 개념을 전제로 함")
needs("FULL OUTER JOIN", ["LEFT OUTER JOIN", "RIGHT OUTER JOIN"],
      "FULL OUTER JOIN = LEFT와 RIGHT OUTER JOIN 결과의 합(중복 제외)이므로 {src} 선행")
req("LEFT OUTER JOIN", "연속 OUTER JOIN", "연속 OUTER JOIN은 OUTER JOIN 결과에 다시 OUTER JOIN을 거는 것")
req("보존 테이블", "OUTER JOIN 조건 위치", "조건 위치에 따라 보존 테이블의 행이 남는지가 달라짐")
req("ON", "OUTER JOIN 조건 위치", "ON 절과 WHERE 절의 역할 차이를 알아야 조건 위치 규칙을 이해")
req("WHERE", "ON vs WHERE", "ON vs WHERE는 WHERE의 후필터 동작을 알아야 이해 가능")

# SQ6 서브쿼리·WITH/CTE
needs("서브쿼리", ["SELECT", "WHERE"], "서브쿼리는 SELECT 결과를 다른 SQL(WHERE 등)의 입력으로 쓰는 구조")
req("서브쿼리", ["단일행 서브쿼리", "다중행 서브쿼리", "스칼라 서브쿼리", "상관 서브쿼리", "인라인 뷰",
               "서브쿼리 ORDER BY 제한"],
    "{dst}은(는) 서브쿼리를 위치/결과 행수/외부 참조로 구분한 유형·규칙")
req("다중행 서브쿼리", ["ANY", "ALL"], "{dst}은(는) 다중행 결과와 비교하는 연산자")
req("단일행 서브쿼리", "스칼라 서브쿼리", "스칼라 서브쿼리는 1행 1열을 반환해야 하는 단일행 서브쿼리의 특수형")
req("상관 서브쿼리", "EXISTS", "EXISTS는 주로 외부 행을 참조하는 상관 서브쿼리로 존재 여부를 판단")
req("EXISTS", "NOT EXISTS", "NOT EXISTS는 EXISTS의 부정")
req("ORDER BY", "서브쿼리 ORDER BY 제한", "서브쿼리 안 ORDER BY 제한 규칙은 ORDER BY 개념 선행")
req("인라인 뷰", "WITH 절", "WITH 절은 이름을 붙여 재사용하는 인라인 뷰")
req("WITH 절", "CTE", "CTE(공통 테이블 표현식)는 WITH 절로 정의")

# SQ7 집합 연산자
req("SELECT", "집합 연산자", "집합 연산자는 두 SELECT 결과 집합을 결합")
req("집합 연산자", ["UNION", "UNION ALL", "INTERSECT", "MINUS", "EXCEPT", "집합 연산자 컬럼 호환성", "집합 연산자 ORDER BY"],
    "{dst}은(는) 집합 연산자 개념을 전제로 함")
# UNION vs UNION ALL is a CONTRASTS pair -> comparison card (cmp_union), not an edge.
needs("집합 연산자 우선순위", ["UNION", "INTERSECT", "MINUS"],
      "우선순위를 따지려면 {src}의 결과를 먼저 알아야 함")
req("ORDER BY", "집합 연산자 ORDER BY", "집합 연산 결과 정렬 규칙은 ORDER BY 개념 선행")

# =============================================================================
# Stage 5 · 집계
# =============================================================================
req("SELECT", "집계 함수", "집계 함수는 SELECT 결과의 여러 행을 하나의 값으로 축약")
req("집계 함수", ["COUNT", "SUM", "AVG", "MIN", "MAX", "NULL 집계", "공집합 집계", "GROUP BY",
                 "WHERE 집계함수 사용 불가", "윈도우 함수", "PIVOT", "MAX() OVER(PARTITION BY)"],
    "{dst}은(는) 집계 함수(여러 행 → 한 값) 개념을 전제로 함")
req("COUNT", ["COUNT(*)", "COUNT(열)", "COUNT(DISTINCT)"], "{dst}은(는) COUNT의 인자 형태별 동작")
req("DISTINCT", "COUNT(DISTINCT)", "COUNT(DISTINCT)는 중복 제거 후 개수")
req("공집합", "공집합 집계", "공집합 집계 규칙은 '결과 행이 없는 상황'을 먼저 알아야 이해")
req("SUM", "SUM(열1+열2) vs SUM(열1)+SUM(열2)", "SUM의 NULL 무시 규칙을 알아야 두 식의 차이를 설명 가능")
req("NULL 산술 연산", "SUM(열1+열2) vs SUM(열1)+SUM(열2)", "행 단위 열1+열2가 NULL이 되는 규칙이 차이의 원인")
needs("문자형 MIN/MAX", ["MIN", "MAX"], "문자형 MIN/MAX는 {src}를 문자열 정렬 순서에 적용")
req("GROUP BY", ["GROUP BY NULL", "GROUP BY 후 ORDER BY 제약", "GROUP BY 확장", "그룹함수 확장",
                 "PARTITION BY", "GROUP BY 후 윈도우 함수", "PIVOT"],
    "{dst}은(는) GROUP BY의 그룹화 개념을 전제로 함")
req("HAVING", "HAVING without GROUP BY", "GROUP BY 없는 HAVING은 HAVING(그룹 필터) 개념의 특수 사례")
req("ORDER BY", "GROUP BY 후 ORDER BY 제약", "GROUP BY 이후 ORDER BY가 참조할 수 있는 대상 규칙")
req("WHERE", "WHERE 집계함수 사용 불가", "WHERE 절이 그룹 이전 행 단계에서 평가된다는 것을 알아야 함")
req("SQL 논리 실행 순서", "WHERE 집계함수 사용 불가", "WHERE가 GROUP BY보다 먼저 평가되는 실행 순서로 설명")
req("그룹함수 확장", ["ROLLUP", "CUBE", "GROUPING SETS"], "{dst}은(는) 그룹함수 확장(소계/총계 생성) 문법")
needs("GROUPING", ["ROLLUP", "CUBE"], "GROUPING은 {src}가 만든 소계 행의 NULL을 구분하는 함수")
req("GROUPING SETS", "전체 총계 ()", "빈 그룹 ()는 GROUPING SETS 안에서 전체 총계를 지정")

# =============================================================================
# Stage 6 · 고급 조회
# =============================================================================
# AG3 윈도우 함수
req("윈도우 함수", "OVER 절", "윈도우 함수는 OVER 절로 계산 범위(윈도우)를 지정")
req("ORDER BY", "OVER 절", "OVER 절 안의 ORDER BY는 정렬 개념을 전제로 함")
req("OVER 절", ["PARTITION BY", "ROWS/RANGE 프레임", "순위 함수", "행 순서 함수", "그룹 내 비율 함수",
               "MAX() OVER(PARTITION BY)"],
    "{dst}은(는) OVER 절 문맥 안에서만 의미를 가짐")
req("PARTITION BY", ["순위 함수", "MAX() OVER(PARTITION BY)"],
    "{dst}은(는) PARTITION BY로 나눈 그룹 단위로 계산됨")
req("순위 함수", ["RANK", "DENSE_RANK", "ROW_NUMBER"],
    "{dst}은(는) 윈도우 함수의 OVER(ORDER BY) 문맥을 전제로 하는 순위 함수")
req("행 순서 함수", ["LAG", "LEAD", "FIRST_VALUE", "LAST_VALUE"],
    "{dst}은(는) 정렬된 윈도우 안에서 다른 행의 값을 가져오는 행 순서 함수")
req("ROWS/RANGE 프레임", "LAST_VALUE",
    "LAST_VALUE는 기본 프레임(…CURRENT ROW)에서 현재 행 값을 돌려주는 함정이 있어 프레임 개념이 선행")
req("그룹 내 비율 함수", ["RATIO_TO_REPORT", "PERCENT_RANK", "CUME_DIST", "NTILE"],
    "{dst}은(는) 그룹 내 비율/분포 함수")
req("RANK", "PERCENT_RANK", "PERCENT_RANK = (RANK - 1) / (파티션 행 수 - 1)")
req("ROWS/RANGE 프레임", ["ROWS", "RANGE", "CURRENT ROW", "UNBOUNDED PRECEDING", "UNBOUNDED FOLLOWING",
                        "PRECEDING/FOLLOWING"],
    "{dst}은(는) 윈도우 프레임 절의 구성 요소")
needs("ROWS PRECEDING/FOLLOWING", ["ROWS", "PRECEDING/FOLLOWING"], "ROWS n PRECEDING/FOLLOWING은 {src}의 조합")
req("RANGE", ["RANGE BETWEEN", "윈도우 RANGE 프레임"], "{dst}은(는) RANGE(값 기준 범위) 프레임의 문법")
needs("RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW", ["RANGE BETWEEN", "UNBOUNDED PRECEDING", "CURRENT ROW"],
      "ORDER BY가 있을 때의 기본 프레임으로, {src}의 조합")
req("윈도우 함수", "GROUP BY 후 윈도우 함수", "GROUP BY 결과 위에 윈도우 함수를 적용하는 순서 규칙")

# AG4 Top-N
req("ORDER BY", "Top-N", "Top-N은 정렬 후 상위 N행을 자르는 패턴")
req("Top-N", ["ROWNUM", "TOP", "FETCH FIRST", "LIMIT"], "{dst}은(는) Top-N을 구현하는 DBMS별 문법")
req("인라인 뷰", "ROWNUM", "ROWNUM은 ORDER BY 이전에 부여되므로 정렬 후 Top-N에는 인라인 뷰가 필요")
needs("WITH TIES", ["TOP", "FETCH FIRST"], "WITH TIES는 {src}에 붙어 마지막 동순위 행까지 포함")

# AG5 PIVOT·UNPIVOT
req("PIVOT·UNPIVOT", ["PIVOT", "UNPIVOT"], "{dst}은(는) 행↔열 재구성 문법")
req("PIVOT", "UNPIVOT", "UNPIVOT은 PIVOT의 역변환(열→행)")

# HQ1 계층형 질의
req("순환 관계(자기참조)", ["계층형 질의", "재귀 CTE"],
    "{dst}은(는) 같은 테이블 안의 부모-자식(자기참조) 구조를 전개")
req("셀프 조인", "계층형 질의", "계층형 질의는 셀프 조인으로 한 단계씩 하던 부모-자식 연결을 반복 전개")
req("계층형 질의", ["START WITH", "CONNECT BY", "LEVEL"], "{dst}은(는) 계층형 질의 문법의 구성 요소")
req("WHERE", "START WITH", "START WITH는 루트 행을 고르는 조건절(WHERE와 같은 조건식)")
req("START WITH", "CONNECT BY", "전개는 START WITH로 정한 루트에서 시작해 CONNECT BY로 자식을 연결하므로 루트 지정을 먼저 학습")
req("CONNECT BY", ["PRIOR", "NOCYCLE", "CONNECT_BY_ISLEAF", "CONNECT_BY_ROOT", "SYS_CONNECT_BY_PATH",
                  "ORDER SIBLINGS BY", "WHERE 후 계층 필터", "계층 전개 NULL 종료", "LEVEL"],
    "{dst}은(는) CONNECT BY로 전개된 계층 결과를 전제로 함")
needs("순방향 계층 전개", ["START WITH", "PRIOR"],
      "전개 방향은 루트(START WITH)와 PRIOR가 붙은 컬럼 위치로 결정되므로 {src} 선행")
needs("역방향 계층 전개", ["START WITH", "PRIOR"],
      "전개 방향은 루트(START WITH)와 PRIOR가 붙은 컬럼 위치로 결정되므로 {src} 선행")
req("START WITH", "CONNECT_BY_ROOT", "CONNECT_BY_ROOT는 START WITH로 정한 루트 행의 값을 반환")
req("ORDER BY", "ORDER SIBLINGS BY", "ORDER SIBLINGS BY는 계층 구조를 유지한 채 형제끼리 ORDER BY")
req("WHERE", "WHERE 후 계층 필터", "계층 전개 후 WHERE가 개별 행만 걸러낸다는 규칙은 WHERE 개념 선행")
req("WHERE 후 계층 필터", "계층형 질의 WHERE 후필터", "같은 규칙의 시험 함정 버전(가지치기 vs 후필터)")
req("CTE", "재귀 CTE", "재귀 CTE는 CTE가 자기 자신을 참조하는 형태")
req("UNION ALL", "재귀 CTE", "재귀 CTE는 앵커 멤버와 재귀 멤버를 UNION ALL로 결합")

# =============================================================================
# Stage 7 · 데이터·객체 관리
# =============================================================================
# MG1 DML
req("DML", ["INSERT", "UPDATE", "DELETE", "MERGE", "트리거"], "{dst}은(는) DML(데이터 조작) 문장/개념")
req("WHERE", ["UPDATE", "DELETE"], "{dst}은(는) WHERE로 대상 행을 지정")
req("INSERT", ["INSERT ALL", "INSERT FIRST", "MERGE"], "{dst}은(는) INSERT 문법을 전제로 함")
req("서브쿼리", ["INSERT ALL", "INSERT FIRST"], "다중 테이블 INSERT는 서브쿼리 결과를 조건별로 분배")
req("UPDATE", "MERGE", "MERGE는 일치하면 UPDATE, 없으면 INSERT하는 문장")
req("MERGE", ["MERGE MATCHED", "MERGE NOT MATCHED", "UPSERT"], "{dst}은(는) MERGE의 구성/용도")
needs("MERGE DELETE", ["MERGE MATCHED", "DELETE"], "MERGE DELETE는 WHEN MATCHED UPDATE 후 조건에 맞는 행을 삭제")

# MG2 DDL·객체
req("DDL", ["CREATE TABLE", "ALTER", "DROP", "TRUNCATE", "RENAME", "CREATE INDEX", "객체명 규칙",
            "Oracle/SQL Server DDL 차이", "VIEW"],
    "{dst}은(는) DDL(객체 정의) 문장/규칙")
req("자료형", "CREATE TABLE", "CREATE TABLE은 각 컬럼의 자료형을 정의")
req("CREATE TABLE", ["DEFAULT", "IDENTITY", "CTAS", "제약조건"], "{dst}은(는) CREATE TABLE 컬럼/테이블 정의의 일부")
req("SELECT", "CTAS", "CTAS는 SELECT 결과로 새 테이블을 만듦")
req("ALTER", "ALTER TABLE", "ALTER TABLE은 ALTER의 테이블 대상 문장")
req("ALTER TABLE", ["ALTER TABLE ADD", "ADD COLUMN", "ADD CONSTRAINT", "ALTER COLUMN", "ALTER/MODIFY", "MODIFY",
                   "DROP COLUMN", "DROP CONSTRAINT", "RENAME COLUMN", "자료형 변경", "DEFAULT 변경"],
    "{dst}은(는) ALTER TABLE의 하위 절")
req("DEFAULT", "DEFAULT 변경", "DEFAULT 변경은 이미 정의된 DEFAULT 값을 바꾸는 것")
req("자료형", "자료형 변경", "자료형 변경 가능 조건은 자료형 개념 선행")
req("DROP", ["DROP 의존성", "CASCADE CONSTRAINTS", "DROP CASCADE", "VIEW 의존성"],
    "{dst}은(는) DROP 동작(객체 삭제)을 전제로 함")
req("RENAME", "RENAME COLUMN", "RENAME COLUMN은 RENAME의 컬럼 대상 형태")
req("CREATE INDEX", ["DROP INDEX", "인덱스"], "{dst}은(는) CREATE INDEX로 만든 인덱스 객체를 다룸")

# MG3 제약조건·참조동작
needs("제약조건", ["PK", "FK"], "제약조건 종류 중 PK/FK는 Stage 1에서 배운 키를 DDL로 구현한 것이므로 {src} 선행")
req("제약조건", ["CHECK", "UNIQUE", "NOT NULL", "데이터 무결성 유지", "CASCADE", "PK 제약 비상속",
                "ADD CONSTRAINT", "DROP CONSTRAINT"],
    "{dst}은(는) 제약조건 개념을 전제로 함")
req("UNIQUE", "UNIQUE 키워드", "UNIQUE 키워드 용법은 UNIQUE 제약 개념 선행")
req("도메인 무결성", "CHECK", "CHECK 제약은 도메인 무결성을 DDL로 구현")
req("참조 무결성", "데이터 무결성 유지", "데이터 무결성 유지 수단(제약/트리거)은 무결성 규칙 선행")
req("데이터 무결성 유지", "트리거", "트리거는 제약조건으로 표현하기 어려운 무결성을 유지하는 수단")
req("CTAS", "PK 제약 비상속", "CTAS가 어떤 제약을 복사하지 않는지는 CTAS 동작 선행")
req("FK", ["CASCADE", "CASCADE CONSTRAINTS", "DROP CASCADE"], "{dst}은(는) FK 참조 관계를 함께 처리하는 옵션")

# MG4 VIEW
req("SELECT", "VIEW", "VIEW는 저장된 SELECT 문")
req("VIEW", "VIEW 의존성", "VIEW 의존성은 VIEW가 기반 테이블을 참조한다는 것을 전제")

# =============================================================================
# Stage 8 · 트랜잭션·권한
# =============================================================================
req("DML", "Transaction", "트랜잭션은 DML 변경을 묶는 논리적 작업 단위")
req("Transaction", ["ACID", "TCL", "AUTO COMMIT", "SQL Server 트랜잭션"], "{dst}은(는) 트랜잭션 개념을 전제로 함")
req("ACID", ["원자성", "일관성", "격리성", "지속성"], "{dst}은(는) ACID 특성의 한 항목")
req("TCL", ["COMMIT", "ROLLBACK", "SAVEPOINT"], "{dst}은(는) TCL(트랜잭션 제어) 명령")
req("ROLLBACK", "ROLLBACK TO SAVEPOINT", "ROLLBACK TO SAVEPOINT는 ROLLBACK의 부분 롤백 형태")
req("COMMIT", ["AUTO COMMIT", "Oracle DDL 자동 커밋"], "{dst}은(는) COMMIT이 언제 일어나는지에 관한 규칙")
req("DDL", "Oracle DDL 자동 커밋", "Oracle이 DDL 전후로 자동 COMMIT한다는 규칙은 DDL 개념 선행")
req("AUTO COMMIT", "SQL Server 트랜잭션", "SQL Server는 기본 AUTO COMMIT 모드로 동작")

req("DCL", ["GRANT", "REVOKE", "ROLE", "객체 권한", "시스템 권한"], "{dst}은(는) DCL(권한 제어) 개념")
needs("GRANT", ["객체 권한", "시스템 권한"], "GRANT로 무엇을 부여하는지 알려면 {src} 종류 선행")
req("객체 권한", "UPDATE 권한", "UPDATE 권한은 객체 권한의 하나")
req("DML", "객체 권한", "객체 권한(SELECT/INSERT/UPDATE/DELETE)은 DML 문장 종류에 대응하므로 DML을 먼저 알아야 함")
req("GRANT", ["TO", "GRANT OPTION", "REVOKE", "ROLE"], "{dst}은(는) GRANT(권한 부여) 동작을 전제로 함")
needs("권한 연쇄 회수", ["GRANT OPTION", "REVOKE"],
      "WITH GRANT OPTION으로 재부여된 권한이 REVOKE 시 연쇄 회수되는 규칙이므로 {src} 선행")
req("REVOKE", "REVOKE RESTRICT", "REVOKE RESTRICT는 REVOKE의 회수 옵션")

# =============================================================================
# Stage 9 · DBMS 방언·시험 함정 통합 (synthetic integration nodes)
# =============================================================================
needs("NULL 처리 DBMS 차이", ["빈 문자열과 NULL(Oracle)", "NVL", "COALESCE", "UNIQUE"],
      "{src}의 NULL 처리 동작을 알아야 Oracle/SQL Server의 NULL 차이를 비교할 수 있음")
needs("NULL 정렬 DBMS 차이", ["Oracle NULL 정렬", "SQL Server NULL 정렬", "NULLS FIRST", "NULLS LAST"],
      "{src} 규칙을 알아야 DBMS별 NULL 정렬 위치를 비교할 수 있음")
needs("Top-N 문법 차이", ["ROWNUM", "TOP", "FETCH FIRST", "WITH TIES"],
      "{src}의 동작(적용 시점·동순위 처리)을 알아야 DBMS별 Top-N 문법을 비교할 수 있음")
needs("차집합 MINUS/EXCEPT 차이", ["MINUS", "EXCEPT"],
      "{src}의 의미를 알아야 차집합 연산자의 DBMS별 이름 차이를 정리할 수 있음")
needs("DDL 커밋 동작 차이", ["Oracle DDL 자동 커밋", "SQL Server 트랜잭션", "TRUNCATE"],
      "{src}의 COMMIT/ROLLBACK 동작을 알아야 DBMS별 DDL 트랜잭션 차이를 비교할 수 있음")
needs("문자열 함수 DBMS 차이", ["LENGTH", "LEN", "CONCAT", "SUBSTR"],
      "{src}의 동작을 알아야 DBMS별 문자열 함수 이름·동작 차이를 비교할 수 있음")
needs("별칭 가시성 종합", ["SELECT 별칭 WHERE 사용 불가", "ORDER BY 별칭", "WHERE 집계함수 사용 불가",
                    "집합 연산자 ORDER BY"],
      "'{src}' 규칙은 별칭·집계가 어느 절에서 보이는지 종합하는 데 필요한 조각")
needs("NULL 함정 종합", ["NOT IN", "IN + NULL", "COUNT(열)", "NULL 산술 연산", "공집합 집계",
                    "SUM(열1+열2) vs SUM(열1)+SUM(열2)", "DISTINCT NULL", "GROUP BY NULL", "NULL 집계"],
      "'{src}'은(는) NULL 함정 총정리에 들어가는 개별 규칙")
needs("OUTER JOIN 필터 위치 종합", ["ON vs WHERE", "OUTER JOIN 조건 위치", "FULL OUTER JOIN",
                              "연속 OUTER JOIN", "Oracle (+) OUTER JOIN"],
      "'{src}'을(를) 알아야 OUTER JOIN 결과(보존 행)를 종합 판단할 수 있음")

# =============================================================================
# Legacy (D7) — hidden by default, but placed so the toggle shows a sensible order
# =============================================================================
req("SELECT", "실행계획", "실행계획은 SELECT 문이 어떻게 수행되는지 보여줌")
req("실행계획", ["실행계획 읽기 순서", "Full Table Scan", "Index Scan", "조인 수행 원리"],
    "{dst}은(는) 실행계획 해석을 전제로 함")
needs("규칙 기반 옵티마이저", ["실행계획"], "옵티마이저는 실행계획을 선택하는 주체")
needs("비용 기반 옵티마이저", ["실행계획"], "옵티마이저는 실행계획을 선택하는 주체")
req("인덱스", ["B-Tree 인덱스", "CLUSTERED INDEX", "FK 인덱스", "IOT", "Index Scan", "UNIQUE INDEX SCAN",
              "NESTED LOOP JOIN"],
    "{dst}은(는) 인덱스 구조/접근 방식을 전제로 함")
req("FK", "FK 인덱스", "FK 인덱스는 FK 컬럼에 거는 인덱스")
req("파티셔닝", ["RANGE 파티션", "LIST 파티션", "HASH 파티션"], "{dst}은(는) 파티셔닝 방식의 하나")
req("슈퍼타입/서브타입", "슈퍼/서브타입 변환", "변환 방식은 슈퍼타입/서브타입 구조 선행")
req("슈퍼/서브타입 변환", "개별 타입", "개별 타입(1:1 타입)은 슈퍼/서브타입 변환 방식의 하나")
req("반정규화", ["컬럼 분할", "테이블 병합", "통계 테이블 추가", "성능 데이터 모델링"],
    "{dst}은(는) 반정규화(성능 목적 구조 변경)의 기법/확장")
req("데이터 독립성", "분산 데이터베이스", "분산 DB의 투명성은 데이터 독립성 개념의 확장")
req("분산 데이터베이스", ["분할 투명성", "위치 투명성", "중복 투명성", "지역사상 투명성"],
    "{dst}은(는) 분산 데이터베이스 투명성의 한 종류")
req("DML", "PL/SQL", "PL/SQL은 SQL(DML)을 절차적 블록으로 감싼 언어")
req("PL/SQL", "PL/SQL 블록", "PL/SQL 블록(DECLARE-BEGIN-EXCEPTION-END)은 PL/SQL 구조")
req("PL/SQL 블록", ["PL/SQL 변수 범위", "CURSOR"], "{dst}은(는) PL/SQL 블록 안에서 정의/사용")
req("CURSOR", "CURSOR OPEN", "커서 사용 순서: 선언 → OPEN")
chain(["CURSOR OPEN", "CURSOR FETCH", "CURSOR CLOSE"], "커서 사용 순서: OPEN → FETCH → CLOSE")
req("JOIN", "조인 수행 원리", "물리 조인 방식은 논리적 JOIN 개념 선행")
req("조인 수행 원리", ["NESTED LOOP JOIN", "Sort Merge Join", "HASH JOIN"], "{dst}은(는) 물리 조인 수행 방식")
req("HASH JOIN", "Hash Join Build/Probe", "Build/Probe 단계는 HASH JOIN의 내부 동작")
req("물리적 데이터 모델링", "성능 데이터 모델링", "성능 데이터 모델링은 물리 설계 단계의 성능 고려")
req("성능 데이터 모델링", ["Row Chaining", "Row Migration"], "{dst}은(는) 성능 모델링에서 다루는 저장 현상")
