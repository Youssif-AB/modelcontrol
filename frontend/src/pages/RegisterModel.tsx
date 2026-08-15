import {
  useState,
  type FormEvent,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router";

import { createModel } from "../api";
import type {
  ModelCreate,
  ModelType,
  RiskTier,
} from "../types";


const INITIAL_FORM: ModelCreate = {
  name: "",
  purpose: "",
  business_area: "",
  owner_email: "",
  model_type: "classification",
  risk_tier: "medium",
};


function RegisterModel() {
  const navigate = useNavigate();

  const [form, setForm] =
    useState<ModelCreate>(INITIAL_FORM);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  function updateTextField(
    field:
      | "name"
      | "purpose"
      | "business_area"
      | "owner_email",
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError(null);

      const created = await createModel(form);

      navigate(`/models/${created.id}`);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to register model.");
      }
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <>
      <div className="page-navigation">
        <Link to="/">
          ← Back to inventory
        </Link>
      </div>

      <header className="detail-header">
        <p className="eyebrow">
          MODEL INVENTORY
        </p>

        <h1>Register Model</h1>

        <p className="subtitle">
          Add a model to the governance inventory.
        </p>
      </header>

      <section className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Model Name

              <input
                required
                value={form.name}
                onChange={(event) =>
                  updateTextField(
                    "name",
                    event.target.value,
                  )
                }
                placeholder="Customer Churn Predictor"
              />
            </label>

            <label>
              Business Area

              <input
                required
                value={form.business_area}
                onChange={(event) =>
                  updateTextField(
                    "business_area",
                    event.target.value,
                  )
                }
                placeholder="Customer Analytics"
              />
            </label>

            <label>
              Owner Email

              <input
                required
                type="email"
                value={form.owner_email}
                onChange={(event) =>
                  updateTextField(
                    "owner_email",
                    event.target.value,
                  )
                }
                placeholder="owner@example.com"
              />
            </label>

            <label>
              Model Type

              <select
                value={form.model_type}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    model_type:
                      event.target.value as ModelType,
                  }))
                }
              >
                <option value="classification">
                  Classification
                </option>

                <option value="regression">
                  Regression
                </option>
              </select>
            </label>

            <label>
              Risk Tier

              <select
                value={form.risk_tier}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    risk_tier:
                      event.target.value as RiskTier,
                  }))
                }
              >
                <option value="low">
                  Low
                </option>

                <option value="medium">
                  Medium
                </option>

                <option value="high">
                  High
                </option>
              </select>
            </label>
          </div>

          <label className="full-width-field">
            Purpose

            <textarea
              required
              value={form.purpose}
              onChange={(event) =>
                updateTextField(
                  "purpose",
                  event.target.value,
                )
              }
              placeholder="Predict customers at risk of cancelling their service."
            />
          </label>

          {error && (
            <p className="error form-error">
              {error}
            </p>
          )}

          <div className="form-actions">
            <Link
              className="cancel-link"
              to="/"
            >
              Cancel
            </Link>

            <button
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? "Registering..."
                : "Register Model"}
            </button>
          </div>
        </form>
      </section>
    </>
  );
}

export default RegisterModel;