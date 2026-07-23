# SQLD 학습 대시보드

## 전체 검증 현황

- Question Node: 50 / 50
- Proposition Node: 200 / 200
- Concept Node: 54 (Tier 1: 15 / Tier 2: 26 / Tier 3: 13) — TCL.md 신규 생성(DCL.md의 Transaction 계층 오류 수정 과정에서 추가)
- 검증 완료 Question: 47 / 50 (Q09는 review_required, Q44·Q45는 duplicated_in_source로 별도 표시)
- OCR 검토 잔여: M01-Q09-O4 (1건, contextual_truth: unresolved) — M01-Q10-O1은 해설 텍스트만으로 확정 가능해 normal로 정정됨
- 원본 중복 인쇄 의심: M01-Q44 ↔ M01-Q45 (전체 4×2=8개 선지)
- 깨진 링크: 0건
- 빈 파일: 0건
- 최종 검증 일시: 2026-07-23

## 보류 항목 (의미론적 개념 감사 후속, 2026-07-23)

- Q09-O2: `contextual_truth: true`의 근거가 "일반적 ERD 지식"(원본·PDF 외부 지식)에 의존함 — 원본 또는 PDF 근거 확인 필요
- Q09-O3: `contextual_truth: true`의 근거가 "해설이 오답으로 지목하지 않음"에만 의존함 — Q09-O4에서 동일한 논리가 이미 근거 부족으로 배척된 바 있어 재검토 필요
- Q09-O4: `contextual_truth: unresolved` 유지 — O2·O3와 동일한 판정 기준을 적용해야 함
- 외부 확인이 필요한 정확한 쟁점: O2(카디널리티), O3(Barker # 기호), O4(IE 엔터티 내부 선 구분)에 서로 다른 증거 기준(직접 해설 인용 vs 일반 지식 vs 부정 부재)이 적용되어 있음. 원본 마인드맵 또는 PDF를 재확인해 세 선지에 동일한 기준을 적용하기 전까지 truth 값을 추가로 변경하지 않는다.

## Q01~Q50 원문 검증 상태

| 문제 | 상태 | 수정 여부 | 비고 |
|---|---|---|---|
| Q01 | verified | 아니오 | 개체 무결성 위반 판단 |
| Q02 | verified | 아니오 | 개념적 데이터 모델링 특징 |
| Q03 | verified | 아니오 | 부분 함수 종속 → 2NF |
| Q04 | verified | 아니오 | 모델링 관점(정규화 관점 함정) |
| Q05 | verified | 아니오 | 엔터티 발생시점 분류 |
| Q06 | verified | 아니오 | 정규화 단계별 작업 |
| Q07 | verified | 아니오 | 외래키 설명 |
| Q08 | verified | 아니오 | 복합 식별자 부분 함수 종속 |
| Q09 | review_required | O4의 contextual_truth를 true→unresolved로 정정 | IE/Barker 표기법, O4는 해설이 다루지 않아 확정 불가 |
| Q10 | verified | O1의 ocr_status를 review_required→normal로 정정 | Barker 식별/비식별 관계, O1은 해설 텍스트만으로 확정 가능(다이어그램 세부 기호는 불필요) |
| Q11 | verified | 아니오 | GROUP BY 없는 SUM과 NULL |
| Q12 | verified | 아니오 | VIEW의 DML 가능 여부 |
| Q13 | verified | 아니오 | NVL과 NULL 대체 |
| Q14 | verified | 아니오 | UNPIVOT NULL 처리 |
| Q15 | verified | 아니오 | 문자형 컬럼 ORDER BY 정렬 |
| Q16 | verified | 아니오 | Oracle 정규표현식 함수 |
| Q17 | verified | 아니오 | SQL 명령어 분류(DCL) |
| Q18 | verified | 아니오 | REPLACE·LOWER 중첩 |
| Q19 | verified | 아니오 | LEFT OUTER JOIN + COUNT |
| Q20 | verified | 아니오 | WHERE절 집계 함수 오류 |
| Q21 | verified | 아니오 | ROLLUP·CUBE·GROUPING SETS |
| Q22 | verified | 아니오 | NOT IN + NULL |
| Q23 | verified | 아니오 | DENSE_RANK |
| Q24 | verified | 아니오 | TOP WITH TIES |
| Q25 | verified | 아니오 | REGEXP_SUBSTR |
| Q26 | verified | 아니오 | ISNULL·NVL·NULLIF·COALESCE |
| Q27 | verified | 아니오 | LEFT OUTER JOIN 특징 |
| Q28 | verified | 아니오 | CONNECT BY 계층 전개 |
| Q29 | verified | 아니오 | 집계 함수와 NULL |
| Q30 | verified | 아니오 | GROUP BY + HAVING 실전 |
| Q31 | verified | 아니오 | WHERE와 HAVING 차이 |
| Q32 | verified | 아니오 | NULL 비교(IS NULL) |
| Q33 | verified | 아니오(직전 세션에서 contextual_truth 오류 수정됨) | ROLLUP 집계 수준 |
| Q34 | verified | 아니오 | 트랜잭션 원자성 |
| Q35 | verified | 아니오 | ROWS BETWEEN 이동 합계 |
| Q36 | verified | 아니오 | ORDER BY 별칭·순서번호 |
| Q37 | verified | 아니오 | NVL·ROUND·LENGTH·MAX |
| Q38 | verified | 아니오 | NVL + SUM |
| Q39 | verified | 아니오 | CROSS JOIN 카티션 곱 |
| Q40 | verified | 아니오 | DDL 자동 커밋 + ROLLBACK |
| Q41 | verified | 아니오 | 서브쿼리 사용 가능 절 |
| Q42 | verified | 아니오 | MINUS 차집합 |
| Q43 | verified | 아니오 | 서브쿼리·EXISTS |
| Q44 | duplicated_in_source | 아니오 | GRANT/REVOKE 연쇄 회수, Q45와 원문 동일 인쇄 |
| Q45 | duplicated_in_source | 아니오 | Q44와 동일 시나리오, 원본 중복 여부 사용자 확인 필요 |
| Q46 | verified | 아니오 | TRUNCATE 특징 |
| Q47 | verified | 아니오 | DROP·DELETE·TRUNCATE 비교 |
| Q48 | verified | 아니오 | MODIFY vs ALTER COLUMN |
| Q49 | verified | 아니오 | SUM/COUNT(*) + NULL |
| Q50 | verified | 아니오 | REGEXP_LIKE 휴대폰 번호 형식 |

## Tier 1 핵심 허브

| Concept | 고유 Question | Proposition | Concept Degree | Bridge | 중심성 해석 |
|---|---:|---:|---:|---|---|
| [[NULL]] | 16 | 47 | 9 | high | 직접 출제와 구조적 중심성이 모두 가장 높은 진짜 허브 |
| [[집계 함수]] | 8 | 23 | 6 | high | 직접 출제도 많고 여러 개념(COUNT, NULL, HAVING)을 연결 |
| [[정규화]] | 5 | 14 | 3 | medium | 직접 출제 많음, 구조적 연결은 중간 |
| [[ERD]] | 2 | 8 | 10 | high | 직접 출제는 적지만 구조적 중심성이 전체 1위 — 빈도≠중심성의 대표 사례 |
| [[DDL]] | 4 | 6 | 7 | high | 직접 출제와 구조적 연결(DROP/TRUNCATE/ALTER/AUTO COMMIT) 모두 높음 |
| [[PK]] | 2 | 4 | 7 | high | 직접 출제는 적으나 데이터모델링↔SQL 구현을 잇는 구조적 허브 |
| [[식별자]] | 2 | 3 | 7 | high | 직접 출제 0, 판단 개입 2 — 순수 구조적 허브에 가까움 |
| [[제약조건]] | 1 | 2 | 7 | high | 직접 출제 0 — PK/FK/CHECK/UNIQUE를 묶는 상위 허브 |
| [[FK]] | 2 | 5 | 6 | high | PK와 짝을 이루는 참조 무결성 허브 — 대시보드에 누락되어 있던 항목을 YAML 기준으로 반영 |
| [[GROUP BY]] | 3 | 8 | 4 | medium | 집계 함수·HAVING과 함께 SQL 실행순서의 축 |
| [[WHERE]] | 3 | 9 | 4 | medium | HAVING과 대조되는 실행순서 허브 |
| [[JOIN]] | 2 | 5 | 5 | medium | OUTER JOIN·CROSS JOIN의 상위 개념 |
| [[Transaction]] | 3 | 4 | 4 | medium | COMMIT·ROLLBACK·ACID가 다루는 대상 개념(TCL이 이를 제어하는 명령어 분류) |
| [[엔터티]] | 1 | 1 | 4 | medium | 직접 출제 0 — 데이터 모델링의 구조적 출발점 |
| [[관계]] | 0 | 0 | 6 | high | 직접 출제·판단 개입 모두 0이지만 관계차수·관계선택성·FK를 연결하는 순수 구조적 허브 |

## Tier 2 주요 적용 개념

| Concept | 고유 Question | 주요 문제 유형 |
|---|---:|---|
| [[DCL]] | 3 | GRANT/REVOKE 권한 전이(Q17, Q44, Q45) |
| [[윈도우 함수]] | 3 | RANK류·ROWS BETWEEN(Q23, Q24, Q35) |
| [[정규표현식 함수]] | 3 | REGEXP_LIKE/SUBSTR/COUNT(Q16, Q25, Q50) |
| [[함수적 종속]] | 3 | 정규화 판단 근거(Q03, Q06, Q08) |
| [[COUNT]] | 3 | NULL 처리 함정(Q19, Q29, Q49) |
| [[HAVING]] | 3 | WHERE 대조(Q20, Q30, Q31) |
| [[ORDER BY]] | 3 | 정렬 기준·NULL 위치(Q15, Q24, Q36) |
| [[DELETE]] | 3 | 삭제 명령 비교(Q46, Q47) |
| [[ROLLBACK]] | 3 | 트랜잭션 흐름 추적(Q40, Q46, Q47) |
| [[OUTER JOIN]] | 2 | LEFT/RIGHT 기준 테이블(Q19, Q27) |
| [[TRUNCATE]] | 2 | DDL 자동 커밋(Q46, Q47) |
| [[그룹함수 확장]] | 2 | ROLLUP/CUBE(Q21, Q33) |
| [[서브쿼리]] | 2 | 사용 가능 절·EXISTS(Q41, Q43) |
| [[DROP]] | 2 | 구조 삭제(Q47) |
| [[참조 무결성]] | 2 | FK 규칙(Q01, Q07) |
| [[비식별 관계]] | 2 | ERD bar 기호(Q10) |
| [[식별 관계]] | 2 | ERD bar 기호(Q10) |
| [[ACID]] | 1 | 원자성 정의(Q34) |
| [[ALTER]] | 1 | MODIFY vs ALTER COLUMN(Q48) |
| [[AUTO COMMIT]] | 1 | Oracle DDL 자동 커밋(Q40) |
| [[VIEW]] | 1 | 단순/복합 뷰 DML(Q12) |
| [[개체 무결성]] | 1 | PK NULL 위반(Q01) |
| [[데이터 모델링 3단계]] | 1 | 개념적/논리적/물리적(Q02) |
| [[COMMIT]] | 1 | 트랜잭션 확정(Q17) |
| [[관계 차수]] | 1 | ERD 카디널리티(Q09) |
| [[TCL]] | 1 | SQL 명령어 분류, Transaction 제어(Q17) — DCL.md 계층 오류 수정 중 신규 생성 |

## Tier 3 세부 규칙

- [[문자형 함수]] (상위: SQL 기본 4. 공통 표현 도구)
- [[CROSS JOIN]] (상위: [[JOIN]])
- [[PIVOT·UNPIVOT]] (상위: 원본 부재, mock-01 보강)
- [[계층형 질의]] (상위: 원본 부재, mock-01 보강)
- [[데이터 모델링 관점]] (상위: [[데이터 모델링 3단계]])
- [[엔터티 분류]] (상위: [[엔터티]])
- [[자료형]] (상위: [[ORDER BY]])
- [[집합 연산자]] (상위: 원본 부재, mock-01 보강)
- [[DML]] (상위: [[DELETE]])
- [[관계 선택성]] (상위: [[관계]])
- [[IN·NOT IN]] (상위: [[WHERE]])
- [[숫자형 함수]] (상위: SQL 기본 4. 공통 표현 도구)
- [[속성]] (상위: [[엔터티]]) — 이번 검증 중 깨진 링크 수정을 위해 신규 생성됨

## 연결망 학습 모드

1. 대시보드에서 Concept Node를 연다.
2. 능동 회상 질문에 답한다.
3. 접힌 답을 확인한다.
4. 연결된 문제를 푼다.
5. 틀린 선지만 Proposition에서 확인한다.
6. Local Graph로 다음 개념에 이동한다.

**Graph View 필터**

개념과 문제 중심:

```
path:"SQLD/Pilot" -path:"SQLD/Pilot/Propositions"
```

전체 선지 포함:

```
path:"SQLD/Pilot"
```

## NULL 분석

- 직접 출제: 9개 문제(Q11, Q13, Q14, Q22, Q26, Q29, Q32, Q38, Q49) — NULL 처리 자체가 핵심 질문
- 판단 개입: 7개 문제(Q01, Q07, Q09, Q19, Q20, Q27, Q37) — 다른 개념(PK, FK, ERD, JOIN 등) 판단에 NULL 규칙이 필요
- Proposition 연결: 47개(선지 단위, 여러 선지가 동일 문제에서 NULL을 함께 언급하며 증폭됨)
- 구조적 중심성: concept_degree 9(전체 2위, ERD 다음)
- 링크 증폭 효과: 16개 문제 × 평균 약 3개 선지가 NULL을 언급 — 문제 수(16) 대비 Proposition 연결(47)이 약 3배로 증폭됨
- 학습 시 주의점: "NULL이 그래프에서 제일 크게 보이는 이유"는 실제로 여러 단원(제약조건, NULL 처리 함수, 비교·논리, 집합·서브쿼리, 집계, JOIN, 정렬)에 걸쳐 반복 응용되기 때문이며, 이는 이기적 교재의 "빈도 중" 표시와 모순되지 않는다 — 교재 빈도는 "NULL 단원"의 직접 출제 횟수를 세지만, Graph 중심성은 다른 단원에서 NULL 규칙이 "보조적으로" 얼마나 자주 쓰이는지까지 반영하기 때문이다.

## 오늘의 학습 순서

1. Tier 1 Concept Node 하나 선택
2. 한 줄 정의와 핵심 규칙을 보지 않고 회상
3. 연결된 Question Node를 정답을 가리고 풀이
4. 틀리거나 헷갈린 Proposition만 확인
5. Concept Node의 능동 회상 질문에 답함
6. 다음 날 같은 Concept을 재시험
