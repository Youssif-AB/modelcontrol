import json
import tempfile
from pathlib import Path

import mlflow

from mlflow import MlflowClient
from mlflow.exceptions import (
    MlflowException,
)

from app.config import settings


EXPERIMENT_NAME = (
    "ModelControl Demo"
)

MODEL_NAME = (
    "DemoChurnModel"
)


def main():
    tracking_uri = (
        settings.mlflow_tracking_uri
    )

    mlflow.set_tracking_uri(
        tracking_uri
    )

    client = MlflowClient(
        tracking_uri=tracking_uri,
        registry_uri=tracking_uri,
    )

    experiment = (
        client.get_experiment_by_name(
            EXPERIMENT_NAME
        )
    )

    if experiment is None:
        experiment_id = (
            client.create_experiment(
                EXPERIMENT_NAME
            )
        )
    else:
        experiment_id = (
            experiment.experiment_id
        )

    with mlflow.start_run(
        experiment_id=experiment_id,
        run_name="demo-churn-v1",
    ) as run:
        mlflow.log_params(
            {
                "algorithm":
                    "gradient_boosting",
                "max_depth": "5",
                "learning_rate": "0.05",
                "training_dataset":
                    "synthetic_churn_v1",
            }
        )

        mlflow.log_metrics(
            {
                "accuracy": 0.887,
                "precision": 0.861,
                "recall": 0.842,
                "f1": 0.851,
            }
        )

        with (
            tempfile.TemporaryDirectory()
            as temp_directory
        ):
            path = (
                Path(temp_directory)
                / "model_metadata.json"
            )

            path.write_text(
                json.dumps(
                    {
                        "model":
                            MODEL_NAME,
                        "purpose":
                            (
                                "Demo customer "
                                "churn model"
                            ),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            mlflow.log_artifact(
                str(path),
                artifact_path="model",
            )

        run_id = run.info.run_id

    try:
        client.get_registered_model(
            MODEL_NAME
        )

    except MlflowException:
        client.create_registered_model(
            MODEL_NAME,
            description=(
                "Demo registered model "
                "used to demonstrate "
                "ModelControl MLflow "
                "integration."
            ),
        )

    existing_versions = (
        client.search_model_versions(
            filter_string=(
                f"name = '{MODEL_NAME}'"
            )
        )
    )

    for version in existing_versions:
        if version.run_id == run_id:
            print(
                "Demo model version "
                "already registered."
            )
            return

    model_version = (
        client.create_model_version(
            name=MODEL_NAME,
            source=(
                f"runs:/{run_id}/model"
            ),
            run_id=run_id,
        )
    )

    print(
        "Created MLflow demo:"
    )
    print(
        f"model={MODEL_NAME}"
    )
    print(
        f"version={model_version.version}"
    )
    print(
        f"run_id={run_id}"
    )


if __name__ == "__main__":
    main()