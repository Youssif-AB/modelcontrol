from tests.conftest import (
    auth_headers,
    login,
)


MODEL_PAYLOAD = {
    "name": "Test Churn Model",
    "purpose": (
        "Predict customers likely "
        "to leave the service"
    ),
    "business_area": "Analytics",
    "owner_email": "owner@test.com",
    "model_type": "classification",
    "risk_tier": "medium",
}


def test_owner_can_create_own_model(
    client,
    owner_user,
):
    token = login(
        client,
        "owner@test.com",
    )

    response = client.post(
        "/models",
        json=MODEL_PAYLOAD,
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    body = response.json()

    assert (
        body["name"]
        == "Test Churn Model"
    )

    assert (
        body["purpose"]
        == MODEL_PAYLOAD["purpose"]
    )

    assert (
        body["lifecycle_status"]
        == "draft"
    )


def test_owner_cannot_create_model_for_other_user(
    client,
    owner_user,
):
    token = login(
        client,
        "owner@test.com",
    )

    payload = {
        **MODEL_PAYLOAD,
        "owner_email":
            "someone@test.com",
    }

    response = client.post(
        "/models",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_reviewer_cannot_create_model(
    client,
    reviewer_user,
):
    token = login(
        client,
        "reviewer@test.com",
    )

    response = client.post(
        "/models",
        json={
            **MODEL_PAYLOAD,
            "owner_email":
                "reviewer@test.com",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_authenticated_user_can_list_models(
    client,
    admin_user,
):
    token = login(
        client,
        "admin@test.com",
    )

    response = client.get(
        "/models",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json() == []