import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { updateLifecycle } from "../api";
import type { ModelRecord } from "../types";
import LifecyclePanel from "./LifecyclePanel";

vi.mock("../api", () => ({ updateLifecycle: vi.fn() }));

const model: ModelRecord = {
  id: 1, name: "Risk Model", purpose: "Governed risk model purpose",
  business_area: "Risk", owner_email: "owner@test.com",
  model_type: "classification", risk_tier: "high",
  lifecycle_status: "under_review", created_at: "2026-08-23T12:00:00Z",
  updated_at: "2026-08-23T12:00:00Z",
};

beforeEach(() => vi.mocked(updateLifecycle).mockReset());

it("requires and submits a rejection reason", async () => {
  const user = userEvent.setup();
  const updated = { ...model, lifecycle_status: "draft" as const };
  vi.mocked(updateLifecycle).mockResolvedValue(updated);
  const onUpdated = vi.fn();
  render(<LifecyclePanel model={model} canManage={false} canReview onUpdated={onUpdated} />);

  await user.click(screen.getByRole("button", { name: "Return to draft" }));
  const reason = screen.getByRole("textbox", { name: "Rejection reason" });
  expect(reason).toBeRequired();
  await user.type(reason, "Missing validation evidence");
  await user.click(screen.getByRole("button", { name: "Confirm Return to draft" }));

  expect(updateLifecycle).toHaveBeenCalledWith(1, "reject", "Missing validation evidence");
  expect(onUpdated).toHaveBeenCalledWith(updated);
});

it("keeps lifecycle controls read-only without permission", () => {
  render(<LifecyclePanel model={model} canManage={false} canReview={false} onUpdated={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "Approve model" })).not.toBeInTheDocument();
  expect(screen.getByText(/No lifecycle action is available/)).toBeInTheDocument();
});
