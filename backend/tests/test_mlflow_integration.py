from app.mlflow_schemas import (
    MLflowRegisteredModelRead,
    MLflowVersionDetails,
    MLflowVersionSummary,
)
from tests.conftest import auth_headers, login
from tests.test_governance import MODEL_PAYLOAD


def create_model(client, token):
    response = client.post(
        "/models",
        json=MODEL_PAYLOAD,
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def test_reviewer_has_read_only_registry_access(
    client,
    reviewer_user,
    monkeypatch,
):
    reviewer_token = login(client, "reviewer@test.com")
    monkeypatch.setattr(
        "app.main.list_mlflow_models",
        lambda: [
            MLflowRegisteredModelRead(
                name="ChurnModel",
                description="Churn risk model",
                versions=[
                    MLflowVersionSummary(
                        name="ChurnModel",
                        version="3",
                        run_id="run-123",
                        source="models:/ChurnModel/3",
                        status="READY",
                    )
                ],
            )
        ],
    )

    response = client.get(
        "/integrations/mlflow/models",
        headers=auth_headers(reviewer_token),
    )

    assert response.status_code == 200
    assert response.json()[0]["versions"][0]["run_id"] == "run-123"


def test_owner_import_persists_structured_provenance(
    client,
    owner_user,
    monkeypatch,
):
    owner_token = login(client, "owner@test.com")
    model = create_model(client, owner_token)
    monkeypatch.setattr(
        "app.main.get_mlflow_version_details",
        lambda model_name, version: MLflowVersionDetails(
            name=model_name,
            version=version,
            run_id="run-456",
            source="s3://models/churn",
            status="READY",
            metrics={"accuracy": 0.91},
            params={"max_depth": "8"},
        ),
    )

    response = client.post(
        f"/models/{model['id']}/versions/import/mlflow",
        json={"model_name": "ChurnModel", "version": "4"},
        headers=auth_headers(owner_token),
    )

    assert response.status_code == 201
    imported = response.json()["version"]
    assert imported["source_type"] == "mlflow"
    assert imported["registered_model_name"] == "ChurnModel"
    assert imported["external_version"] == "4"
    assert imported["run_id"] == "run-456"
    assert imported["metrics"] == {"accuracy": 0.91}
    assert imported["params"] == {"max_depth": "8"}


def test_reviewer_cannot_import_mlflow_version(
    client,
    owner_user,
    reviewer_user,
):
    owner_token = login(client, "owner@test.com")
    reviewer_token = login(client, "reviewer@test.com")
    model = create_model(client, owner_token)

    response = client.post(
        f"/models/{model['id']}/versions/import/mlflow",
        json={"model_name": "ChurnModel", "version": "1"},
        headers=auth_headers(reviewer_token),
    )

    assert response.status_code == 403
