import type {
  AuditEvent,
  Finding,
  FindingCreate,
  LifecycleAction,
  ModelCreate,
  ModelRecord,
  ModelVersion,
  ModelVersionCreate,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";


async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    let message = "Something went wrong";

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json();
}


export async function fetchModels(): Promise<ModelRecord[]> {
  const response = await fetch(`${API_BASE_URL}/models`);

  return handleResponse<ModelRecord[]>(response);
}


export async function fetchModel(
  modelId: number,
): Promise<ModelRecord> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}`,
  );

  return handleResponse<ModelRecord>(response);
}


export async function createModel(
  model: ModelCreate,
): Promise<ModelRecord> {
  const response = await fetch(`${API_BASE_URL}/models`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(model),
  });

  return handleResponse<ModelRecord>(response);
}

export async function fetchVersions(
  modelId: number,
): Promise<ModelVersion[]> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/versions`,
  );

  return handleResponse<ModelVersion[]>(response);
}


export async function createVersion(
  modelId: number,
  version: ModelVersionCreate,
): Promise<ModelVersion> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/versions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(version),
    },
  );

  return handleResponse<ModelVersion>(response);
}


export async function updateLifecycle(
  modelId: number,
  action: LifecycleAction,
): Promise<ModelRecord> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/lifecycle`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ action }),
    },
  );

  return handleResponse<ModelRecord>(response);
}

export async function fetchFindings(
  modelId: number,
): Promise<Finding[]> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/findings`,
  );

  return handleResponse<Finding[]>(response);
}


export async function createFinding(
  modelId: number,
  finding: FindingCreate,
): Promise<Finding> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/findings`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(finding),
    },
  );

  return handleResponse<Finding>(response);
}


export async function resolveFinding(
  findingId: number,
  resolutionNotes: string,
): Promise<Finding> {
  const response = await fetch(
    `${API_BASE_URL}/findings/${findingId}/resolve`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resolution_notes: resolutionNotes,
      }),
    },
  );

  return handleResponse<Finding>(response);
}


export async function fetchAudit(
  modelId: number,
): Promise<AuditEvent[]> {
  const response = await fetch(
    `${API_BASE_URL}/models/${modelId}/audit`,
  );

  return handleResponse<AuditEvent[]>(response);
}