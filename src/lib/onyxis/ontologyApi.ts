export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json();
}

export async function fetchOntologyState(): Promise<any> {
  const response = await fetch(`${API_BASE}/api/state`, { cache: "no-store" });
  return handleResponse(response);
}

export async function fetchOntologyInspect(): Promise<any> {
  const response = await fetch(`${API_BASE}/api/inspect`, { cache: "no-store" });
  return handleResponse(response);
}

export async function postOntologyControl(action: string, payload?: Record<string, unknown>): Promise<any> {
  const response = await fetch(`${API_BASE}/api/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, payload }),
  });
  return handleResponse(response);
}
