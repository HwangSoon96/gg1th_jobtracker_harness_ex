# JobTracker 프로젝트 정의

> 주제: 취업준비생의 채용 지원 현황을 관리하는 웹 애플리케이션
> 용도: 하네스 엔지니어링 실습. 이 문서는 CLAUDE.md 작성의 재료다.

---

## 1. 목표

취업준비생이 브라우저에서 지원 건을 등록하고, 목록으로 조회하고, 진행 상태를 바꿀 수 있는 MVP를 만든다.

| 구성 요소 | 상태 | 문서 위치 |
|---|---|---|
| 입력 데이터 | 확정 | 2장 |
| 기능 요구사항 | 확정 | 3장, 4장 |
| 화면 설계 | 확정 | 5장 |
| 완료 조건 | 확정 | 7장 |

---

## 2. 입력 데이터

위치: `input_data/`

| 파일 | 내용 | 용도 |
|---|---|---|
| `seed_applications.csv` | 기존 지원 내역 12건 (표 형식) | 초기 데이터 |
| `seed_applications.json` | CSV와 동일한 내용 (JSON 형식) | 초기 데이터. 둘 중 하나만 쓴다 |
| `api_test_cases.json` | 요청과 기대 응답 12개 케이스 | 완료 판정 기준 (테스트) |

필드: `id`, `company_name`, `position`, `applied_date`, `status`, `notes`

---

## 3. 기능 정의

| ID | 기능 | 설명 | 근거 |
|---|---|---|---|
| F1 | 초기 데이터 적재 | 앱을 처음 실행하면 기존 지원 내역 12건이 들어 있다 | seed 파일, TC04·TC10의 전제 |
| F2 | 지원 등록 | 회사명, 직무, 지원일, 상태, 메모를 입력해 새 지원 건을 저장한다 | TC01 |
| F3 | 지원 목록 조회 | 저장된 지원 건 전체를 지원일 최신순으로 본다 | 요구사항 |
| F4 | 지원 상태 변경 | 지원 건 하나의 진행 상태를 바꾼다 | TC10~12 |
| F5 | 화면 | 목록 화면과 등록 화면에서 F2~F4를 사용한다 | 요구사항 |

---

## 4. 데이터 규칙

| 규칙 | 내용 | 관련 TC |
|---|---|---|
| 필수 입력 | 회사명, 직무, 지원일, 상태는 필수이고 메모는 선택이다 | TC02 |
| 공백 처리 | 양끝 공백을 제거하며, 공백만 있으면 입력이 없는 것으로 본다 | TC03 |
| 날짜 | YYYY-MM-DD 형식이어야 하고 실제로 있는 날짜여야 한다 | TC08, TC09 |
| 미래 날짜 | 허용하지 않는다 | 추가 테스트 필요 (8장 참고) |
| 상태 값 | 아래 5개 코드 중 하나 | TC07, TC12 |
| 중복 금지 | 회사명과 직무 조합이 같으면 등록하지 않는다. 공백을 제거하고 대소문자를 무시하고 비교한다 | TC04~06 |
| 저장 | SQLite에 저장되어 서버를 재시작해도 남는다 | 요구사항 |

### 상태 코드

저장은 영문 코드, 화면 표시는 한글로 한다.

| 저장 값 | 화면 표시 |
|---|---|
| `applied` | 지원완료 |
| `document_passed` | 서류합격 |
| `interview` | 면접 |
| `final_passed` | 최종합격 |
| `rejected` | 불합격 |

---

## 5. 화면 설계

### 화면 1. 목록 (`/`)

- 지원 건 표: 회사명, 직무, 지원일, 상태, 메모
- 지원일 최신순으로 정렬한다
- 행마다 상태 변경 드롭다운과 [변경] 버튼
- 상단에 [새 지원 등록] 버튼

### 화면 2. 등록 (`/new`)

- 입력 칸: 회사명, 직무, 지원일(날짜 선택), 상태(드롭다운), 메모
- [저장]을 누르면 목록 화면으로 이동한다
- 오류(중복, 형식 오류)가 나면 같은 화면에 메시지를 표시한다

### 공통 규칙

- 순수 HTML과 Jinja2 템플릿만 쓴다
- 화면은 위 2개만 만든다

---

## 6. 하지 않을 것

범위를 명시하지 않으면 AI가 기능을 덧붙이는 경우가 많다.

- 지원 건 수정과 삭제
- 로그인과 회원 관리
- 검색, 필터, 통계
- React 같은 프론트엔드 프레임워크

---

## 7. 완료 조건

| ID | 조건 | 확인 방법 |
|---|---|---|
| D1 | `api_test_cases.json` 12개 케이스를 옮긴 pytest가 전부 통과한다 | `uv run pytest` |
| D2 | 브라우저에서 목록 조회, 등록, 상태 변경이 된다 | 서버 실행 후 직접 확인 |
| D3 | 서버를 재시작해도 데이터가 SQLite에 남아 있다 | 등록 → 재시작 → 목록 확인 |

---

## 8. 결정 사항

| 항목 | 결정 | 이유 |
|---|---|---|
| 목록 정렬 | 지원일 최신순 | 최근 지원 건을 가장 자주 확인한다 |
| 상태 표시 | 화면은 한글, 저장은 영문 코드 | 사용자는 읽기 쉽고, 데이터와 테스트는 그대로 쓸 수 있다 |
| 미래 날짜 | 허용하지 않음 | 지원일은 이미 지원한 날이므로 미래일 수 없다 |

미래 날짜 금지는 `api_test_cases.json`에 없는 규칙이다. 유지하려면 테스트 케이스를 하나 추가해야 한다. 추가하지 않을 경우 "허용"으로 바꾼다.

---

## 9. 기술 스택

| 구분 | 선택 |
|---|---|
| 언어 | Python 3.12 |
| 패키지 관리 | uv |
| 웹 프레임워크 | FastAPI + Uvicorn |
| HTML 렌더링 | Jinja2 (`Jinja2Templates`) |
| 폼 입력 | `Form(...)` + `python-multipart` |
| DB | SQLite (`sqlite3` 표준 모듈) |
| 테스트 | pytest + `fastapi.testclient.TestClient` (`httpx` 필요) |

사용 도구(Agent): Claude Code CLI, Claude Desktop, Codex CLI, Codex Desktop 등

---

## 10. 개발 환경

### 가상환경

```powershell
cd E:\happymaker_lab\harness_eng\jobtracker-harness

uv init --bare --python 3.12    # pyproject.toml만 생성
uv python pin 3.12              # .python-version으로 3.12 고정
uv venv                         # .venv 생성
uv run python --version         # Python 3.12.x 확인
```

### 라이브러리

```powershell
uv add fastapi uvicorn jinja2 python-multipart
uv add --dev pytest httpx
```

---

## 11. 폴더 구조 (완성 시점)

처음부터 전부 만들지 않는다. 단계를 진행하면서 하나씩 생긴다.

```
jobtracker-harness/
├─ CLAUDE.md                # 가이드: 항상 읽는 규칙
├─ .claude/
│  ├─ settings.json         # 집행: 권한, Hook 등록
│  └─ hooks/verify_stop.py  # 집행: 종료 전 테스트 강제
├─ input_data/              # 입력 데이터 3개
├─ app/
│  ├─ main.py               # 라우트
│  ├─ db.py                 # get_db(), 스키마 생성, 시드 적재
│  └─ templates/            # index.html, new.html
├─ tests/                   # 센서: api_test_cases.json 기반, AI 수정 금지
│  ├─ conftest.py           # dependency_overrides + tmp_path DB
│  └─ test_app.py
├─ pyproject.toml
├─ uv.lock
└─ .python-version
```
