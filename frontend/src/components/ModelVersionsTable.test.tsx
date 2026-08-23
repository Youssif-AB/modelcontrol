import {
  render,
  screen,
} from "@testing-library/react";
import {
  expect,
  it,
} from "vitest";

import ModelVersionsTable
  from "./ModelVersionsTable";
import type {
  ModelVersion,
} from "../types";


it("renders legacy MLflow descriptions without raw metadata", () => {
  const version: ModelVersion = {
    id: 1,
    model_id: 1,
    version_number: 1,
    description: (
      "Imported from MLflow. registered_model=PCValueAnalyzer; "
      + "mlflow_version=1; run_id=legacy-run; "
      + "source=models:/PCValueAnalyzer/1; "
      + 'metrics={"mae": 12.5}; params={"depth": "8"}'
    ),
    source_type: "manual",
    registered_model_name: null,
    external_version: null,
    run_id: null,
    artifact_source: null,
    metrics: null,
    params: null,
    created_at: "2026-08-23T12:00:00Z",
  };

  render(<ModelVersionsTable versions={[version]} />);

  expect(screen.getByText(
    "Imported from MLflow — PCValueAnalyzer v1",
  )).toBeInTheDocument();

  for (const rawMetadata of [
    "metrics={",
    "params={",
    "run_id=",
    "source=models:",
  ]) {
    expect(
      screen.queryByText(
        (_, element) =>
          element?.textContent.includes(rawMetadata)
          ?? false,
      ),
    ).not.toBeInTheDocument();
  }
});
