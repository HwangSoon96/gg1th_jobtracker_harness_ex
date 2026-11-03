# JobTracker

취업준비생이 지원한 회사와 진행 상태를 등록, 조회, 변경하는 웹 애플리케이션이다.
상세 정의는 [`docs/JobTracker_프로젝트정의.md`](docs/JobTracker_프로젝트정의.md)를 따른다.

## 기술 스택

- Python 3.12
- FastAPI + Uvicorn, Jinja2 템플릿
- SQLite (`sqlite3` 표준 모듈)
- 패키지 관리: [uv](https://docs.astral.sh/uv/)

## 환경 셋업

### 1. uv 설치

아직 없다면 설치한다.

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 확인:

```powershell
uv --version
```

### 2. 프로젝트 의존성 설치

저장소 루트(이 파일이 있는 위치)에서 실행한다. `pyproject.toml`과 `uv.lock`에 명시된 Python 3.12와 의존성(FastAPI, Uvicorn, Jinja2 등)을 가상환경(`.venv`)에 설치한다.

```powershell
uv sync
```

## 프로그램 실행

### 서버 실행

```powershell
uv run uvicorn app.main:app --reload
```

- 브라우저에서 `http://127.0.0.1:8000` 접속
- 처음 실행 시 DB(`jobtracker.db`)가 비어 있으면 `input_data/seed_applications.json`의 12건이 자동으로 적재된다
- DB 파일은 저장소 루트에 생성되며, 서버를 재시작해도 데이터가 유지된다

> **포트 충돌 시**: `[WinError 10013] 액세스 권한에 의해 숨겨진 소켓에 액세스를 시도했습니다` 오류가 나면 8000번 포트를 다른 프로세스(Windows 시스템 서비스 등)가 이미 사용 중인 경우다. `netstat -ano | findstr ":8000"`으로 점유 중인지 확인하고, 아래처럼 다른 포트를 지정해서 실행한다.
>
> ```powershell
> uv run uvicorn app.main:app --reload --port 8080
> ```

### 화면

| 경로 | 설명 |
|---|---|
| `/` | 지원 목록 (지원일 최신순, 상태 변경 가능) |
| `/new` | 새 지원 등록 |

### 테스트 실행

```powershell
uv run pytest
```

테스트는 실제 DB 파일이 아닌 임시 DB(`tmp_path`)를 사용하므로 `jobtracker.db`에 영향을 주지 않는다.

## 폴더 구조

```
app/
  main.py        # 라우트
  db.py          # DB 연결, 스키마 생성, 시드 적재
  validation.py  # 입력 검증
  templates/     # index.html, new.html
tests/           # pytest 테스트
input_data/      # 시드 데이터, API 테스트 케이스 (읽기 전용)
docs/            # 프로젝트 정의서
```
