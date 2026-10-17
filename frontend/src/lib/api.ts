// A sandbox grouping key only. All submitted records and session associations live in SQLite.
let sessionKey: string | undefined;
function sandboxSession() {
  if (sessionKey) return sessionKey;
  try {
    sessionKey = localStorage.getItem("habitat.v6.session") || crypto.randomUUID();
    localStorage.setItem("habitat.v6.session", sessionKey);
  } catch {
    sessionKey ??= crypto.randomUUID();
  }
  return sessionKey;
}

type RequestOptions = { idempotencyKey?: string };
async function request(path: string, body?: unknown, options?: RequestOptions): Promise<any> {
  try {
    const response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      headers: { "Content-Type": "application/json", "X-Sandbox-Session": sandboxSession(), ...(options?.idempotencyKey ? {"Idempotency-Key": options.idempotencyKey} : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(20000),
    });
    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Service unavailable" }));
      const detail = Array.isArray(error.detail)
        ? error.detail
            .map(
              (e: any) => `${e.loc?.slice(1).join(".") || "Input"}: ${e.msg}`,
            )
            .join("; ")
        : error.detail;
      throw new Error(detail || `Request failed (${response.status})`);
    }
    return response.json();
  } catch (error) {
    if (error instanceof TypeError)
      throw new Error(
        "Could not reach the local API. Start the backend and retry.",
        { cause: error },
      );
    if (error instanceof DOMException && error.name === "TimeoutError")
      throw new Error(
        "The request timed out. No successful action has been confirmed; check the case before retrying.",
        { cause: error },
      );
    throw error;
  }
}

const inFlight = new Map<string, Promise<any>>();
export function api(path: string, body?: unknown, options?: RequestOptions): Promise<any> {
  if (body !== undefined) return request(path, body, options);
  const existing = inFlight.get(path);
  if (existing) return existing;
  const promise = request(path);
  inFlight.set(path, promise);
  promise.then(
    () => inFlight.delete(path),
    () => inFlight.delete(path),
  );
  return promise;
}
