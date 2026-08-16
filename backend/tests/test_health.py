def test_health_check(client):
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_models_require_authentication(
    client,
):
    response = client.get(
        "/models"
    )

    assert response.status_code == 401