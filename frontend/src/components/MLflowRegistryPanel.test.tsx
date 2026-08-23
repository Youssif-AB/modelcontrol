import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { fetchMLflowModels, importMLflowVersion } from "../api";
import MLflowRegistryPanel from "./MLflowRegistryPanel";

vi.mock("../api", () => ({
  fetchMLflowModels: vi.fn(),
  importMLflowVersion: vi.fn(),
}));

const registry = [{
  name: "ChurnModel",
  description: "Churn model",
  versions: [{
    name: "ChurnModel", version: "2", run_id: "run-2",
    source: "models:/ChurnModel/2", status: "READY",
  }],
}];

beforeEach(() => {
  vi.mocked(fetchMLflowModels).mockReset();
  vi.mocked(importMLflowVersion).mockReset();
});

it("loads provenance and imports a selected version", async () => {
  const user = userEvent.setup();
  vi.mocked(fetchMLflowModels).mockResolvedValue(registry);
  const result = {
    version: {
      id: 8, model_id: 1, version_number: 3, description: "Imported",
      source_type: "mlflow" as const, registered_model_name: "ChurnModel",
      external_version: "2", run_id: "run-2",
      artifact_source: "models:/ChurnModel/2", metrics: { accuracy: 0.9 },
      params: { depth: "4" }, created_at: "2026-08-23T12:00:00Z",
    },
    mlflow: {
      ...registry[0].versions[0],
      metrics: { accuracy: 0.9 }, params: { depth: "4" },
    },
  };
  vi.mocked(importMLflowVersion).mockResolvedValue(result);
  const onImported = vi.fn();
  render(<MLflowRegistryPanel modelId={1} canImport onImported={onImported} />);

  await user.click(await screen.findByRole("button", { name: /Version 2/ }));
  expect(screen.getByText("run-2")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Import into ModelControl" }));
  expect(onImported).toHaveBeenCalledWith(result);
  expect(await screen.findByText("Imported as v3")).toBeInTheDocument();
});

it("shows MLflow failures", async () => {
  vi.mocked(fetchMLflowModels).mockRejectedValue(new Error("MLflow unavailable"));
  render(<MLflowRegistryPanel modelId={1} canImport onImported={vi.fn()} />);
  expect(await screen.findByText("MLflow unavailable")).toBeInTheDocument();
});
