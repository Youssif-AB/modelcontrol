from mlflow import MlflowClient
from mlflow.exceptions import (
    MlflowException,
)

from app.config import settings
from app.mlflow_schemas import (
    MLflowRegisteredModelRead,
    MLflowVersionDetails,
    MLflowVersionSummary,
)


class MLflowIntegrationError(
    RuntimeError
):
    pass


def get_mlflow_client() -> MlflowClient:
    return MlflowClient(
        tracking_uri=(
            settings.mlflow_tracking_uri
        ),
        registry_uri=(
            settings.mlflow_tracking_uri
        ),
    )


def list_mlflow_models(
) -> list[MLflowRegisteredModelRead]:
    try:
        client = get_mlflow_client()

        registered_models = list(
            client.search_registered_models(
                max_results=100
            )
        )

        model_versions = list(
            client.search_model_versions(
                max_results=1000
            )
        )

    except MlflowException as exc:
        raise MLflowIntegrationError(
            "Unable to communicate with MLflow"
        ) from exc

    versions_by_model: dict[
        str,
        list[MLflowVersionSummary],
    ] = {}

    for version in model_versions:
        versions_by_model.setdefault(
            version.name,
            [],
        ).append(
            MLflowVersionSummary(
                name=version.name,
                version=str(
                    version.version
                ),
                run_id=version.run_id,
                source=version.source,
                status=(
                    str(version.status)
                    if version.status
                    else None
                ),
            )
        )

    for versions in (
        versions_by_model.values()
    ):
        versions.sort(
            key=lambda item: int(
                item.version
            )
            if item.version.isdigit()
            else 0
        )

    result = []

    for registered_model in sorted(
        registered_models,
        key=lambda item: item.name,
    ):
        result.append(
            MLflowRegisteredModelRead(
                name=registered_model.name,
                description=(
                    registered_model.description
                ),
                versions=(
                    versions_by_model.get(
                        registered_model.name,
                        [],
                    )
                ),
            )
        )

    return result


def get_mlflow_version_details(
    model_name: str,
    version: str,
) -> MLflowVersionDetails:
    try:
        client = get_mlflow_client()

        model_version = (
            client.get_model_version(
                model_name,
                version,
            )
        )

        metrics: dict[
            str,
            float,
        ] = {}

        params: dict[
            str,
            str,
        ] = {}

        if model_version.run_id:
            run = client.get_run(
                model_version.run_id
            )

            metrics = dict(
                run.data.metrics
            )

            params = dict(
                run.data.params
            )

        return MLflowVersionDetails(
            name=model_version.name,
            version=str(
                model_version.version
            ),
            run_id=(
                model_version.run_id
            ),
            source=(
                model_version.source
            ),
            status=(
                str(model_version.status)
                if model_version.status
                else None
            ),
            metrics=metrics,
            params=params,
        )

    except MlflowException as exc:
        raise MLflowIntegrationError(
            "Unable to retrieve MLflow "
            "model version"
        ) from exc