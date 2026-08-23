import { expect, it, vi } from "vitest";
import {
  fetchModels,
  getAccessToken,
  SESSION_EXPIRED_EVENT,
  setAccessToken,
} from "./api";

it("clears an expired session and broadcasts a 401", async () => {
  setAccessToken("expired-token");
  const listener = vi.fn();
  window.addEventListener(SESSION_EXPIRED_EVENT, listener);
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ detail: "Session expired" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    }),
  );

  await expect(fetchModels()).rejects.toThrow("Session expired");
  expect(getAccessToken()).toBeNull();
  expect(listener).toHaveBeenCalledOnce();
  window.removeEventListener(SESSION_EXPIRED_EVENT, listener);
});
