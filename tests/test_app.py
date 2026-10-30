from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.app import app


EXPECTED_FIELDS = {
    "description",
    "schedule",
    "location",
    "days",
    "max_participants",
    "participants",
}
TEXT_FIELDS = ("description", "schedule", "location")
WEEKDAYS = {
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
}


@pytest.fixture
def activity_records() -> dict[str, dict[str, Any]]:
    with TestClient(app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, dict)
    return records


def test_activities_include_expected_fields(
    activity_records: dict[str, dict[str, Any]],
) -> None:
    assert activity_records

    for name, activity in activity_records.items():
        assert name.strip()
        assert isinstance(activity, dict)
        assert EXPECTED_FIELDS <= activity.keys()


@pytest.mark.parametrize("field", TEXT_FIELDS)
def test_activity_text_fields_are_non_empty(
    activity_records: dict[str, dict[str, Any]], field: str
) -> None:
    for name, activity in activity_records.items():
        value = activity[field]
        assert isinstance(value, str), f"{name}.{field} must be a string"
        assert value.strip(), f"{name}.{field} must not be empty"


def test_activity_days_are_valid_weekdays(
    activity_records: dict[str, dict[str, Any]],
) -> None:
    for name, activity in activity_records.items():
        days = activity["days"]
        assert isinstance(days, list), f"{name}.days must be a list"
        assert days, f"{name}.days must contain at least one day"
        assert all(
            isinstance(day, str) and day in WEEKDAYS for day in days
        ), f"{name}.days must contain valid weekday names"


def test_participant_fields_have_valid_types_and_capacity(
    activity_records: dict[str, dict[str, Any]],
) -> None:
    for name, activity in activity_records.items():
        max_participants = activity["max_participants"]
        participants = activity["participants"]

        assert type(max_participants) is int, (
            f"{name}.max_participants must be an integer"
        )
        assert max_participants > 0, f"{name}.max_participants must be positive"
        assert isinstance(participants, list), (
            f"{name}.participants must be a list"
        )
        assert all(
            isinstance(participant, str) and participant.strip()
            for participant in participants
        ), f"{name}.participants must contain non-empty strings"
        assert len(participants) <= max_participants, (
            f"{name} has more participants than its capacity"
        )
