import re
import sqlite3
from datetime import date

STATUS_LABELS = {
    "applied": "지원완료",
    "document_passed": "서류합격",
    "interview": "면접",
    "final_passed": "최종합격",
    "rejected": "불합격",
}

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(Exception):
    pass


def clean_required_text(value: str | None, field_label: str) -> str:
    if value is None:
        raise ValidationError(f"{field_label}은 필수 입력값입니다.")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_label}은 필수 입력값입니다.")
    return cleaned


def validate_applied_date(value: str | None) -> str:
    cleaned = clean_required_text(value, "지원일")
    if not _DATE_PATTERN.match(cleaned):
        raise ValidationError("지원일은 YYYY-MM-DD 형식이어야 합니다.")
    try:
        parsed = date.fromisoformat(cleaned)
    except ValueError:
        raise ValidationError("지원일이 실제로 존재하지 않는 날짜입니다.")
    if parsed > date.today():
        raise ValidationError("지원일은 미래 날짜일 수 없습니다.")
    return cleaned


def validate_status(value: str | None) -> str:
    cleaned = clean_required_text(value, "상태")
    if cleaned not in STATUS_LABELS:
        raise ValidationError("허용되지 않은 상태 값입니다.")
    return cleaned


def validate_application_payload(
    company_name: str | None,
    position: str | None,
    applied_date: str | None,
    status: str | None,
    notes: str | None,
) -> dict:
    cleaned_notes = notes.strip() if notes is not None else None
    return {
        "company_name": clean_required_text(company_name, "회사명"),
        "position": clean_required_text(position, "직무"),
        "applied_date": validate_applied_date(applied_date),
        "status": validate_status(status),
        "notes": cleaned_notes if cleaned_notes else None,
    }


def is_duplicate(
    connection: sqlite3.Connection, company_name: str, position: str
) -> bool:
    normalized_company = company_name.strip().lower()
    normalized_position = position.strip().lower()
    rows = connection.execute(
        "SELECT company_name, position FROM applications"
    ).fetchall()
    for row in rows:
        if (
            row["company_name"].strip().lower() == normalized_company
            and row["position"].strip().lower() == normalized_position
        ):
            return True
    return False
