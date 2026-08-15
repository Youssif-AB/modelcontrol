import type {
  ModelCreate,
  ModelRecord,
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