from tests.conftest import (
    auth_headers,
    login,
)


def test_login_returns_token(
    client,
    admin_user,
):
    response = client.post(
        "/auth/login",
        data={
            "username":
                "admin@test.com",

            "password":
                "TestPassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_invalid_password_is_rejected(
    client,
    admin_user,
):
    response = client.post(
        "/auth/login",
        data={
            "username":
                "admin@test.com",

            "password":
                "wrong-password",
        },
    )

    assert response.status_code == 401


def test_auth_me_returns_user(
    client,
    owner_user,
):
    token = login(
        client,
        "owner@test.com",
    )

    response = client.get(
        "/auth/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["email"]
        == "owner@test.com"
    )

    assert (
        body["role"]
        == "model_owner"
    )