import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = {
        name: {
            **details,
            "participants": list(details["participants"]),
        }
        for name, details in app_module.activities.items()
    }
    app_module.activities.clear()
    app_module.activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_unregister_participant_removes_email(client):
    activity_name = "Chess Club"
    email = "student@example.com"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
