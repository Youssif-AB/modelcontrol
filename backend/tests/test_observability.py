import uuid


def test_readiness_check(
    client,
):
    response = client.get(
        "/ready"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready"
    }


def test_response_has_request_id(
    client,
):
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None

    uuid.UUID(request_id)


def test_existing_request_id_is_preserved(
    client,
):
    request_id = (
        "integration-test-request-id"
    )

    response = client.get(
        "/health",
        headers={
            "X-Request-ID": request_id
        },
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "X-Request-ID"
        ]
        == request_id
    )


def test_metrics_endpoint(
    client,
):
    client.get("/health")

    response = client.get(
        "/metrics"
    )

    assert response.status_code == 200

    assert (
        "modelcontrol_http_requests_total"
        in response.text
    )

    assert (
        "modelcontrol_http_request_duration_seconds"
        in response.text
    )