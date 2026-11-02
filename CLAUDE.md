# JobTracker: 채용 지원 현황 관리 웹앱

취업준비생이 지원한 회사와 진행 상태를 등록, 조회, 변경하는 웹 애플리케이션이다.
상세 정의는 `docs/JobTracker_프로젝트정의.md`를 따른다. 이 파일과 충돌하면 정의서가 우선이다.

## 기술 스택

- Python 3.12, uv로 패키지 관리 (`pip` 직접 사용 금지, 추가 설치는 `uv add`)
- FastAPI + Uvicorn, Jinja2 템플릿, SQLite(`sqlite3` 표준 모듈)
- 테스트: pytest + `fastapi.testclient.TestClient`
- 프론트엔드 프레임워크(React 등), ORM, 외부 DB는 쓰지 않는다

## 명령

- 서버 실행: `uv run uvicorn app.main:app --reload`
- 테스트: `uv run pytest`

## 폴더 구조

- `app/main.py`: 라우트
- `app/db.py`: `get_db()` 의존성, 스키마 생성, 시드 적재
- `app/templates/`: `index.html`(목록), `new.html`(등록)
- `tests/`: `input_data/api_test_cases.json` 기반 테스트
- `input_data/`: 입력 데이터 (읽기 전용)

## 데이터

필드: `id`, `company_name`, `position`, `applied_date`, `status`, `notes`

- 시드: 앱 시작 시 DB가 비어 있으면 `input_data/seed_applications.json` 12건을 적재한다
- 필수: `company_name`, `position`, `applied_date`, `status` / 선택: `notes`
- 문자열은 양끝 공백을 제거하고 저장한다. 제거 후 빈 문자열이면 422
- `applied_date`: `YYYY-MM-DD` 형식이고 실제로 있는 날짜여야 한다. 미래 날짜는 거부한다. 위반 시 422
- 중복: `company_name` + `position` 조합이 같으면 409. 공백 제거, 대소문자 무시 후 비교한다

### 상태 코드

저장은 영문 코드, 화면 표시는 한글. 이 밖의 값은 422.

| 코드 | 화면 표시 |
|---|---|
| `applied` | 지원완료 |
| `document_passed` | 서류합격 |
| `interview` | 면접 |
| `final_passed` | 최종합격 |
| `rejected` | 불합격 |

## API

| 메서드 | 경로 | 성공 | 실패 |
|---|---|---|---|
| GET | `/api/applications` | 200, 지원일 최신순 목록 | |
| POST | `/api/applications` | 201 | 422 입력 오류, 409 중복 |
| PATCH | `/api/applications/{id}/status` | 200 | 404 없는 ID, 422 상태 값 오류 |

요청과 응답의 기준은 `input_data/api_test_cases.json`이다.

## 화면

- `/` 목록: 지원 건 표(회사명, 직무, 지원일, 상태, 메모), 지원일 최신순, 행마다 상태 드롭다운과 [변경] 버튼, 상단 [새 지원 등록] 버튼
- `/new` 등록: 입력 칸 5개와 [저장] 버튼. 성공하면 `/`로 이동, 오류는 같은 화면에 메시지로 표시
- 화면과 API는 같은 검증 로직을 쓴다
- 화면은 이 2개만 만든다

## 하지 않을 것

- 지원 건 수정과 삭제
- 로그인과 회원 관리
- 검색, 필터, 통계
- 정의서에 없는 기능 추가

## 작업 규칙

- `input_data/`는 수정하지 않는다
- `tests/`는 수정하지 않는다. 테스트가 실패하면 테스트가 아니라 앱 코드를 고친다
- 테스트는 실제 DB 파일을 쓰지 않는다. `dependency_overrides`와 `tmp_path`로 만든 임시 DB를 쓴다

## 완료 기준

아래를 모두 만족해야 완료라고 보고한다. 하나라도 실패하면 완료라고 말하지 않는다.

1. `uv run pytest`가 전부 통과한다
2. 브라우저에서 목록 조회, 등록, 상태 변경이 된다
3. 서버를 재시작해도 데이터가 SQLite에 남아 있다
