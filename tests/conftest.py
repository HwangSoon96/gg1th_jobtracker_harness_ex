import json
import sqlite3
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app


ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    database_path = tmp_path / "test_applications.db"
    seed_path = ROOT_DIR / "input_data" / "seed_applications.json"
    with seed_path.open(encoding="utf-8") as seed_file:
        seed_applications = json.load(seed_file)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                position TEXT NOT NULL,
                applied_date TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
            """
        )
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

    def override_get_db() -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
