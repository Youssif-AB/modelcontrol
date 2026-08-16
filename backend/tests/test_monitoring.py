import pytest

from tests.conftest import (
    auth_headers,
    login,
)


MODEL_PAYLOAD = {
    "name": "Monitoring Test Model",
    "purpose": (
        "Test model performance "
        "monitoring"
    ),
    "business_area": "Analytics",
    "owner_email": "owner@test.com",
    "model_type": "classification",
    "risk_tier": "medium",
}


def create_model(
    client,
    owner_token,
):
    response = client.post(
        "/models",
        json=MODEL_PAYLOAD,
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 201

    return response.json()


@pytest.mark.parametrize(
    (
        "current_value",
        "expected_status",
    ),
    [
        (0.88, "healthy"),
        (0.84, "warning"),
        (0.78, "critical"),
    ],
)
def test_accuracy_monitoring_thresholds(
    client,
    owner_user,
    current_value,
    expected_status,
):
    owner_token = login(
        client,
        "owner@test.com",
    )

    model = create_model(
        client,
        owner_token,
    )

    response = client.post(
        (
            f"/models/"
            f"{model['id']}/monitoring"
        ),
        json={
            "metric_name": "accuracy",
            "baseline_value": 0.90,
            "current_value":
                current_value,

            "direction":
                "higher_is_better",

            "warning_threshold": 0.05,
            "critical_threshold": 0.10,
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 201

    assert (
        response.json()["status"]
        == expected_status
    )


def test_lower_is_better_metric(
    client,
    owner_user,
):
    owner_token = login(
        client,
        "owner@test.com",
    )

    model = create_model(
        client,
        owner_token,
    )

    response = client.post(
        (
            f"/models/"
            f"{model['id']}/monitoring"
        ),
        json={
            "metric_name": "rmse",
            "baseline_value": 10,
            "current_value": 12,
            "direction":
                "lower_is_better",

            "warning_threshold": 0.05,
            "critical_threshold": 0.10,
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "critical"

    assert body["degradation"] == pytest.approx(
        0.2
    )


def test_critical_threshold_must_exceed_warning(
    client,
    owner_user,
):
    owner_token = login(
        client,
        "owner@test.com",
    )

    model = create_model(
        client,
        owner_token,
    )

    response = client.post(
        (
            f"/models/"
            f"{model['id']}/monitoring"
        ),
        json={
            "metric_name": "accuracy",
            "baseline_value": 0.9,
            "current_value": 0.8,
            "direction":
                "higher_is_better",

            "warning_threshold": 0.10,
            "critical_threshold": 0.05,
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 422


def test_reviewer_cannot_record_monitoring(
    client,
    owner_user,
    reviewer_user,
):
    owner_token = login(
        client,
        "owner@test.com",
    )

    reviewer_token = login(
        client,
        "reviewer@test.com",
    )

    model = create_model(
        client,
        owner_token,
    )

    response = client.post(
        (
            f"/models/"
            f"{model['id']}/monitoring"
        ),
        json={
            "metric_name": "accuracy",
            "baseline_value": 0.9,
            "current_value": 0.88,
            "direction":
                "higher_is_better",

            "warning_threshold": 0.05,
            "critical_threshold": 0.10,
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    assert response.status_code == 403