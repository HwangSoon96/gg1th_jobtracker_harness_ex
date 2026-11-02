import json
import sqlite3
from pathlib import Path
from typing import Iterator

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "jobtracker.db"
SEED_PATH = ROOT_DIR / "input_data" / "seed_applications.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    position TEXT NOT NULL,
    applied_date TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
)
"""


def _ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(SCHEMA)
    connection.commit()


def _seed_if_empty(connection: sqlite3.Connection) -> None:
    count = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    if count > 0:
        return
    with SEED_PATH.open(encoding="utf-8") as seed_file:
        seed_applications = json.load(seed_file)
    connection.executemany(
        """
        INSERT INTO applications (
            id, company_name, position, applied_date, status, notes
        ) VALUES (
            :id, :company_name, :position, :applied_date, :status, :notes
        )
        """,
        seed_applications,
    )
    connection.commit()


def get_db() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        _ensure_schema(connection)
        _seed_if_empty(connection)
        yield connection
    finally:
        connection.close()
