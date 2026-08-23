import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { fetchAudit } from "../api";
import AuditPanel from "./AuditPanel";

vi.mock("../api", () => ({ fetchAudit: vi.fn() }));

it("searches readable audit history", async () => {
  const user = userEvent.setup();
  vi.mocked(fetchAudit).mockResolvedValue([
    { id: 1, model_id: 1, event_type: "model_created", description: "Model registered", actor_email: "owner@test.com", created_at: "2026-08-22T12:00:00Z" },
    { id: 2, model_id: 1, event_type: "lifecycle_changed", description: "Approved after validation", actor_email: "reviewer@test.com", created_at: "2026-08-23T12:00:00Z" },
  ]);
  render(<AuditPanel modelId={1} refreshToken={0} />);

  expect(await screen.findByText("Approved after validation")).toBeInTheDocument();
  await user.type(screen.getByRole("searchbox", { name: "Search history" }), "owner@test.com");
  expect(screen.getByText("Model registered")).toBeInTheDocument();
  expect(screen.queryByText("Approved after validation")).not.toBeInTheDocument();
});
