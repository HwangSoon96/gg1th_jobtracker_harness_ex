import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.db import get_db
from app.validation import (
    STATUS_LABELS,
    ValidationError,
    is_duplicate,
    validate_application_payload,
    validate_status,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ApplicationIn(BaseModel):
    company_name: str | None = None
    position: str | None = None
    applied_date: str | None = None
    status: str | None = None
    notes: str | None = None


class StatusUpdateIn(BaseModel):
    status: str | None = None


def _list_applications(connection: sqlite3.Connection) -> list[dict]:
    rows = connection.execute(
        "SELECT * FROM applications ORDER BY applied_date DESC, id DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def _insert_application(connection: sqlite3.Connection, cleaned: dict) -> dict:
    cursor = connection.execute(
        """
        INSERT INTO applications (company_name, position, applied_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            cleaned["company_name"],
            cleaned["position"],
            cleaned["applied_date"],
            cleaned["status"],
            cleaned["notes"],
        ),
    )
    connection.commit()
    row = connection.execute(
        "SELECT * FROM applications WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return dict(row)


@app.get("/api/applications")
def api_list_applications(connection: sqlite3.Connection = Depends(get_db)):
    return _list_applications(connection)


@app.post("/api/applications", status_code=201)
def api_create_application(
    payload: ApplicationIn, connection: sqlite3.Connection = Depends(get_db)
):
    try:
        cleaned = validate_application_payload(
            payload.company_name,
            payload.position,
            payload.applied_date,
            payload.status,
            payload.notes,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    if is_duplicate(connection, cleaned["company_name"], cleaned["position"]):
        raise HTTPException(status_code=409, detail="이미 등록된 지원 건입니다.")

    return _insert_application(connection, cleaned)


@app.patch("/api/applications/{application_id}/status")
def api_update_status(
    application_id: int,
    payload: StatusUpdateIn,
    connection: sqlite3.Connection = Depends(get_db),
):
    row = connection.execute(
        "SELECT * FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="해당 지원 건을 찾을 수 없습니다.")

    try:
        cleaned_status = validate_status(payload.status)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    connection.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (cleaned_status, application_id),
    )
    connection.commit()
    updated = connection.execute(
        "SELECT * FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    return dict(updated)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, connection: sqlite3.Connection = Depends(get_db)):
    applications = _list_applications(connection)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"applications": applications, "status_labels": STATUS_LABELS},
    )


@app.post("/applications/{application_id}/status")
def web_update_status(
    application_id: int,
    status: str = Form(""),
    connection: sqlite3.Connection = Depends(get_db),
):
    row = connection.execute(
        "SELECT * FROM applications WHERE id = ?", (application_id,)
    ).fetchone()
    if row is not None:
        try:
            cleaned_status = validate_status(status)
        except ValidationError:
            cleaned_status = None
        if cleaned_status is not None:
            connection.execute(
                "UPDATE applications SET status = ? WHERE id = ?",
                (cleaned_status, application_id),
            )
            connection.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/new", response_class=HTMLResponse)
def new_form(request: Request):
    return templates.TemplateResponse(
        request,
        "new.html",
        {"status_labels": STATUS_LABELS, "errors": [], "form_data": {}},
    )


@app.post("/new", response_class=HTMLResponse)
def create_application_form(
    request: Request,
    company_name: str = Form(""),
    position: str = Form(""),
    applied_date: str = Form(""),
    status: str = Form(""),
    notes: str = Form(""),
    connection: sqlite3.Connection = Depends(get_db),
):
    form_data = {
        "company_name": company_name,
        "position": position,
        "applied_date": applied_date,
        "status": status,
        "notes": notes,
    }
    try:
        cleaned = validate_application_payload(
            company_name, position, applied_date, status, notes
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "new.html",
            {
                "status_labels": STATUS_LABELS,
                "errors": [str(exc)],
                "form_data": form_data,
            },
            status_code=422,
        )

    if is_duplicate(connection, cleaned["company_name"], cleaned["position"]):
        return templates.TemplateResponse(
            request,
            "new.html",
            {
                "status_labels": STATUS_LABELS,
                "errors": ["이미 등록된 지원 건입니다."],
                "form_data": form_data,
            },
            status_code=409,
        )

    _insert_application(connection, cleaned)
    return RedirectResponse(url="/", status_code=303)
