import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


CASES_PATH = (
    Path(__file__).resolve().parents[1] / "input_data" / "api_test_cases.json"
)
with CASES_PATH.open(encoding="utf-8") as cases_file:
    API_TEST_CASES = json.load(cases_file)


@pytest.mark.parametrize(
    "case",
    API_TEST_CASES,
    ids=[case["id"] for case in API_TEST_CASES],
)
def test_api_test_cases(case: dict[str, Any], client: TestClient) -> None:
    request = getattr(client, case["method"].lower())
    response = request(case["path"], json=case["body"])

    assert response.status_code == case["expected_status"], (
        f'{case["id"]}: {case["expected"]}'
    )

    if case["id"] == "TC01":
        applications = client.get("/api/applications").json()
        assert any(
            application["company_name"] == case["body"]["company_name"]
            and application["position"] == case["body"]["position"]
            for application in applications
        )
    elif case["id"] == "TC10":
        applications = client.get("/api/applications").json()
        application = next(
            application for application in applications if application["id"] == 1
        )
        assert application["status"] == case["body"]["status"]


def test_TC13_rejects_future_applied_date(client: TestClient) -> None:
    response = client.post(
        "/api/applications",
        json={
            "company_name": "미래지원테크",
            "position": "테스트 엔지니어",
            "applied_date": (date.today() + timedelta(days=1)).isoformat(),
            "status": "applied",
        },
    )

    assert response.status_code == 422
