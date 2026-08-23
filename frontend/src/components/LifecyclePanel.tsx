import {
  useState,
  type FormEvent,
} from "react";

import { updateLifecycle } from "../api";
import type {
  LifecycleAction,
  LifecycleStatus,
  ModelRecord,
} from "../types";


interface LifecyclePanelProps {
  model: ModelRecord;
  canManage: boolean;
  canReview: boolean;
  onUpdated: (model: ModelRecord) => void;
}


const LIFECYCLE_STEPS: Array<{
  status: LifecycleStatus;
  label: string;
}> = [
  { status: "draft", label: "Draft" },
  { status: "under_review", label: "Under review" },
  { status: "approved", label: "Approved" },
  { status: "retired", label: "Retired" },
];


const ACTION_DETAILS: Record<
  LifecycleAction,
  { label: string; prompt: string }
> = {
  submit_for_review: {
    label: "Submit for review",
    prompt: "Confirm that this model is ready for governance review.",
  },
  approve: {
    label: "Approve model",
    prompt: "Confirm that the model meets the current review requirements.",
  },
  reject: {
    label: "Return to draft",
    prompt: "Explain what the model owner must address before resubmission.",
  },
  retire: {
    label: "Retire model",
    prompt: "Confirm that this model should no longer be active.",
  },
};


function LifecyclePanel({
  model,
  canManage,
  canReview,
  onUpdated,
}: LifecyclePanelProps) {
  const [pendingAction, setPendingAction] =
    useState<LifecycleAction | null>(null);
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const currentIndex = LIFECYCLE_STEPS.findIndex(
    (step) => step.status === model.lifecycle_status,
  );

  let actions: LifecycleAction[] = [];

  if (model.lifecycle_status === "draft" && canManage) {
    actions = ["submit_for_review"];
  } else if (
    model.lifecycle_status === "under_review" &&
    canReview
  ) {
    actions = ["approve", "reject"];
  } else if (
    model.lifecycle_status === "approved" &&
    canManage
  ) {
    actions = ["retire"];
  }

  function chooseAction(action: LifecycleAction) {
    setPendingAction(action);
    setNote("");
    setError(null);
    setSuccess(null);
  }

  async function confirmAction(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!pendingAction || submitting) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const updated = await updateLifecycle(
        model.id,
        pendingAction,
        note,
      );

      setSuccess(
        `${ACTION_DETAILS[pendingAction].label} completed.`,
      );
      setPendingAction(null);
      setNote("");
      onUpdated(updated);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update the lifecycle.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="lifecycle-panel">
      <div className="section-heading">
        <div>
          <h2>Lifecycle review</h2>
          <p>
            Current governance state and permitted next actions.
          </p>
        </div>
      </div>

      <ol className="lifecycle-track" aria-label="Model lifecycle">
        {LIFECYCLE_STEPS.map((step, index) => (
          <li
            className={
              index === currentIndex
                ? "current"
                : index < currentIndex
                  ? "complete"
                  : "upcoming"
            }
            key={step.status}
            aria-current={
              index === currentIndex ? "step" : undefined
            }
          >
            <span>{index + 1}</span>
            {step.label}
          </li>
        ))}
      </ol>

      {actions.length > 0 ? (
        <div className="lifecycle-actions">
          <strong>Available next actions</strong>
          <div>
            {actions.map((action) => (
              <button
                className={
                  action === "reject" || action === "retire"
                    ? "secondary-button"
                    : undefined
                }
                disabled={submitting}
                key={action}
                type="button"
                onClick={() => chooseAction(action)}
              >
                {ACTION_DETAILS[action].label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p className="permission-note">
          No lifecycle action is available for your role in the
          current state.
        </p>
      )}

      {pendingAction && (
        <form
          className="lifecycle-confirmation"
          onSubmit={confirmAction}
        >
          <h3>{ACTION_DETAILS[pendingAction].label}</h3>
          <p>{ACTION_DETAILS[pendingAction].prompt}</p>

          <label>
            {pendingAction === "reject"
              ? "Rejection reason"
              : "Review note (optional)"}
            <textarea
              required={pendingAction === "reject"}
              minLength={pendingAction === "reject" ? 3 : undefined}
              maxLength={1000}
              value={note}
              onChange={(event) => setNote(event.target.value)}
            />
          </label>

          <div className="form-actions">
            <button
              className="secondary-button"
              disabled={submitting}
              type="button"
              onClick={() => setPendingAction(null)}
            >
              Cancel
            </button>
            <button disabled={submitting} type="submit">
              {submitting
                ? "Updating lifecycle..."
                : `Confirm ${ACTION_DETAILS[pendingAction].label}`}
            </button>
          </div>
        </form>
      )}

      {error && <p className="error" role="alert">{error}</p>}
      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}
    </section>
  );
}


export default LifecyclePanel;
