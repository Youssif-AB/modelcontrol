import type {
  AuditEvent,
  Finding,
  FindingCreate,
  LifecycleAction,
  MLflowImportRequest,
  MLflowImportResult,
  MLflowRegisteredModel,
  ModelCreate,
  ModelRecord,
  ModelVersion,
  ModelVersionCreate,
  MonitoringCreate,
  MonitoringRecord,
  TokenResponse,
  UserRecord,
} from "./types";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

const TOKEN_KEY =
  "modelcontrol_access_token";

export const SESSION_EXPIRED_EVENT =
  "modelcontrol:session-expired";


export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}


export function setAccessToken(
  token: string,
): void {
  sessionStorage.setItem(
    TOKEN_KEY,
    token,
  );
}


export function clearAccessToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}


async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    let message = "Something went wrong";

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        message = body.detail
          .map((item: { msg?: string }) => item.msg)
          .filter(Boolean)
          .join("; ") || message;
      }
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json();
}


async function authenticatedFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const headers =
    new Headers(options.headers);

  const token = getAccessToken();

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  );

  if (response.status === 401) {
    clearAccessToken();
    window.dispatchEvent(
      new Event(SESSION_EXPIRED_EVENT),
    );
  }

  return response;
}


export async function loginUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams();

  body.set("username", email);
  body.set("password", password);

  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body,
    },
  );

  return handleResponse<TokenResponse>(
    response,
  );
}


export async function fetchCurrentUser():
Promise<UserRecord> {
  const response =
    await authenticatedFetch(
      "/auth/me",
    );

  return handleResponse<UserRecord>(
    response,
  );
}


export async function fetchModels():
Promise<ModelRecord[]> {
  const response =
    await authenticatedFetch(
      "/models",
    );

  return handleResponse<ModelRecord[]>(
    response,
  );
}


export async function fetchModel(
  modelId: number,
): Promise<ModelRecord> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}`,
    );

  return handleResponse<ModelRecord>(
    response,
  );
}


export async function createModel(
  model: ModelCreate,
): Promise<ModelRecord> {
  const response =
    await authenticatedFetch(
      "/models",
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(model),
      },
    );

  return handleResponse<ModelRecord>(
    response,
  );
}


export async function fetchVersions(
  modelId: number,
): Promise<ModelVersion[]> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/versions`,
    );

  return handleResponse<ModelVersion[]>(
    response,
  );
}


export async function createVersion(
  modelId: number,
  version: ModelVersionCreate,
): Promise<ModelVersion> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/versions`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(version),
      },
    );

  return handleResponse<ModelVersion>(
    response,
  );
}


export async function updateLifecycle(
  modelId: number,
  action: LifecycleAction,
  note?: string,
): Promise<ModelRecord> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/lifecycle`,
      {
        method: "PATCH",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          action,
          note: note || null,
        }),
      },
    );

  return handleResponse<ModelRecord>(
    response,
  );
}


export async function fetchFindings(
  modelId: number,
): Promise<Finding[]> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/findings`,
    );

  return handleResponse<Finding[]>(
    response,
  );
}


export async function createFinding(
  modelId: number,
  finding: FindingCreate,
): Promise<Finding> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/findings`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(finding),
      },
    );

  return handleResponse<Finding>(
    response,
  );
}


export async function resolveFinding(
  findingId: number,
  resolutionNotes: string,
): Promise<Finding> {
  const response =
    await authenticatedFetch(
      `/findings/${findingId}/resolve`,
      {
        method: "PATCH",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          resolution_notes:
            resolutionNotes,
        }),
      },
    );

  return handleResponse<Finding>(
    response,
  );
}


export async function fetchAudit(
  modelId: number,
): Promise<AuditEvent[]> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/audit`,
    );

  return handleResponse<AuditEvent[]>(
    response,
  );
}


export async function fetchMonitoring(
  modelId: number,
): Promise<MonitoringRecord[]> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/monitoring`,
    );

  return handleResponse<
    MonitoringRecord[]
  >(response);
}


export async function createMonitoringRecord(
  modelId: number,
  monitoring: MonitoringCreate,
): Promise<MonitoringRecord> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/monitoring`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          monitoring,
        ),
      },
    );

  return handleResponse<MonitoringRecord>(
    response,
  );
}


export async function fetchMLflowModels():
Promise<MLflowRegisteredModel[]> {
  const response =
    await authenticatedFetch(
      "/integrations/mlflow/models",
    );

  return handleResponse<
    MLflowRegisteredModel[]
  >(response);
}


export async function importMLflowVersion(
  modelId: number,
  request: MLflowImportRequest,
): Promise<MLflowImportResult> {
  const response =
    await authenticatedFetch(
      `/models/${modelId}/versions/import/mlflow`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(request),
      },
    );

  return handleResponse<MLflowImportResult>(
    response,
  );
}
