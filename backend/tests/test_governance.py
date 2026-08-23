from tests.conftest import (
    auth_headers,
    login,
)


MODEL_PAYLOAD = {
    "name": "Governance Test Model",
    "purpose": (
        "Test lifecycle and "
        "review governance"
    ),
    "business_area": "Risk",
    "owner_email": "owner@test.com",
    "model_type": "classification",
    "risk_tier": "high",
}


def create_model(
    client,
    token,
):
    response = client.post(
        "/models",
        json=MODEL_PAYLOAD,
        headers=auth_headers(token),
    )

    assert response.status_code == 201

    return response.json()


def test_owner_can_add_version(
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
            f"{model['id']}/versions"
        ),
        json={
            "version_number": 1,
            "description":
                "Initial candidate version",
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 201

    assert (
        response.json()[
            "version_number"
        ]
        == 1
    )


def test_reviewer_cannot_add_version(
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
            f"{model['id']}/versions"
        ),
        json={
            "version_number": 1,
            "description":
                "Should not be allowed",
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    assert response.status_code == 403


def test_owner_submits_and_reviewer_approves(
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

    submit_response = client.patch(
        (
            f"/models/"
            f"{model['id']}/lifecycle"
        ),
        json={
            "action":
                "submit_for_review"
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert (
        submit_response.status_code
        == 200
    )

    assert (
        submit_response.json()[
            "lifecycle_status"
        ]
        == "under_review"
    )

    approve_response = client.patch(
        (
            f"/models/"
            f"{model['id']}/lifecycle"
        ),
        json={
            "action": "approve"
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    assert (
        approve_response.status_code
        == 200
    )

    assert (
        approve_response.json()[
            "lifecycle_status"
        ]
        == "approved"
    )


def test_owner_cannot_approve_own_model(
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

    client.patch(
        (
            f"/models/"
            f"{model['id']}/lifecycle"
        ),
        json={
            "action":
                "submit_for_review"
        },
        headers=auth_headers(
            owner_token
        ),
    )

    response = client.patch(
        (
            f"/models/"
            f"{model['id']}/lifecycle"
        ),
        json={
            "action": "approve"
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 403


def test_rejection_requires_reason_and_audits_actor(
    client,
    owner_user,
    reviewer_user,
):
    owner_token = login(client, "owner@test.com")
    reviewer_token = login(client, "reviewer@test.com")
    model = create_model(client, owner_token)

    client.patch(
        f"/models/{model['id']}/lifecycle",
        json={"action": "submit_for_review"},
        headers=auth_headers(owner_token),
    )

    missing_reason = client.patch(
        f"/models/{model['id']}/lifecycle",
        json={"action": "reject"},
        headers=auth_headers(reviewer_token),
    )

    assert missing_reason.status_code == 422

    rejected = client.patch(
        f"/models/{model['id']}/lifecycle",
        json={
            "action": "reject",
            "note": "Validation evidence is incomplete.",
        },
        headers=auth_headers(reviewer_token),
    )

    assert rejected.status_code == 200
    assert rejected.json()["lifecycle_status"] == "draft"

    audit = client.get(
        f"/models/{model['id']}/audit",
        headers=auth_headers(owner_token),
    ).json()
    event = audit[-1]

    assert event["actor_email"] == "reviewer@test.com"
    assert "Validation evidence is incomplete." in event["description"]


def test_invalid_lifecycle_transition_is_rejected(
    client,
    owner_user,
):
    owner_token = login(client, "owner@test.com")
    model = create_model(client, owner_token)

    response = client.patch(
        f"/models/{model['id']}/lifecycle",
        json={"action": "retire", "note": "Too early"},
        headers=auth_headers(owner_token),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot retire model from draft status"
    )


def test_reviewer_can_create_finding(
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
            f"{model['id']}/findings"
        ),
        json={
            "title":
                "Validation gap",

            "description":
                "Latest validation evidence "
                "has not been documented.",

            "severity": "high",
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    assert response.status_code == 201

    assert (
        response.json()["status"]
        == "open"
    )


def test_owner_can_resolve_finding(
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

    finding_response = client.post(
        (
            f"/models/"
            f"{model['id']}/findings"
        ),
        json={
            "title":
                "Documentation gap",

            "description":
                "Required validation "
                "documentation is missing.",

            "severity": "medium",
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    finding_id = (
        finding_response.json()["id"]
    )

    response = client.patch(
        (
            f"/findings/"
            f"{finding_id}/resolve"
        ),
        json={
            "resolution_notes":
                "Documentation was added "
                "and reviewed."
        },
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "resolved"

    assert (
        body["resolution_notes"]
        == (
            "Documentation was added "
            "and reviewed."
        )
    )


def test_governance_actions_create_audit_events(
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

    client.post(
        (
            f"/models/"
            f"{model['id']}/versions"
        ),
        json={
            "version_number": 1,
            "description":
                "Initial model version",
        },
        headers=auth_headers(
            owner_token
        ),
    )

    client.patch(
        (
            f"/models/"
            f"{model['id']}/lifecycle"
        ),
        json={
            "action":
                "submit_for_review"
        },
        headers=auth_headers(
            owner_token
        ),
    )

    client.post(
        (
            f"/models/"
            f"{model['id']}/findings"
        ),
        json={
            "title":
                "Review finding",

            "description":
                "A governance issue was "
                "identified during review.",

            "severity": "low",
        },
        headers=auth_headers(
            reviewer_token
        ),
    )

    response = client.get(
        (
            f"/models/"
            f"{model['id']}/audit"
        ),
        headers=auth_headers(
            owner_token
        ),
    )

    assert response.status_code == 200

    events = response.json()

    event_types = [
        event["event_type"]
        for event in events
    ]

    assert "model_created" in event_types
    assert "version_created" in event_types
    assert "lifecycle_changed" in event_types
    assert "finding_created" in event_types

def test_duplicate_model_version_is_rejected(
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

    payload = {
        "version_number": 1,
        "description": "Initial candidate version",
    }

    first_response = client.post(
        f"/models/{model['id']}/versions",
        json=payload,
        headers=auth_headers(owner_token),
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        f"/models/{model['id']}/versions",
        json=payload,
        headers=auth_headers(owner_token),
    )

    assert duplicate_response.status_code == 409

    assert duplicate_response.json()["detail"] == (
        "Version 1 already exists for this model"
    )
