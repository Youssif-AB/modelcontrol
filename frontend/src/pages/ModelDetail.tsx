import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router";

import { fetchModel } from "../api";
import type { ModelRecord } from "../types";


function ModelDetail() {
  const { modelId } = useParams();

  const [model, setModel] =
    useState<ModelRecord | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    async function loadModel() {
      const parsedId = Number(modelId);

      if (
        !modelId ||
        !Number.isInteger(parsedId) ||
        parsedId <= 0
      ) {
        setError("Invalid model ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const data = await fetchModel(parsedId);

        setModel(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Unable to load model.");
        }
      } finally {
        setLoading(false);
      }
    }

    loadModel();
  }, [modelId]);


  return (
    <>
      <div className="page-navigation">
        <Link to="/">
          ← Back to inventory
        </Link>
      </div>

      {loading && (
        <p className="content-message">
          Loading model...
        </p>
      )}

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {!loading && !error && model && (
        <>
          <header className="detail-header">
            <div>
              <p className="eyebrow">
                MODEL #{model.id}
              </p>

              <h1>{model.name}</h1>

              <p className="subtitle">
                {model.purpose}
              </p>
            </div>

            <div className="detail-badges">
              <span
                className={`badge ${model.risk_tier}`}
              >
                {model.risk_tier} risk
              </span>

              <span className="badge">
                {model.lifecycle_status.replace(
                  "_",
                  " ",
                )}
              </span>
            </div>
          </header>

          <section className="detail-grid">
            <div className="detail-card">
              <span>Business Area</span>
              <strong>
                {model.business_area}
              </strong>
            </div>

            <div className="detail-card">
              <span>Model Type</span>
              <strong>
                {model.model_type}
              </strong>
            </div>

            <div className="detail-card">
              <span>Owner</span>
              <strong>
                {model.owner_email}
              </strong>
            </div>

            <div className="detail-card">
              <span>Lifecycle</span>
              <strong>
                {model.lifecycle_status.replace(
                  "_",
                  " ",
                )}
              </strong>
            </div>
          </section>

          <section className="governance-section">
            <div className="section-heading">
              <div>
                <h2>Governance</h2>

                <p>
                  Versions, lifecycle reviews,
                  findings, monitoring, and audit
                  history will be managed here.
                </p>
              </div>
            </div>

            <div className="governance-grid">
              <div className="feature-card">
                <h3>Versions</h3>
                <p>
                  Track registered versions of this
                  model.
                </p>
              </div>

              <div className="feature-card">
                <h3>Lifecycle</h3>
                <p>
                  Submit, approve, reject, and
                  retire models.
                </p>
              </div>

              <div className="feature-card">
                <h3>Findings</h3>
                <p>
                  Track governance and validation
                  issues.
                </p>
              </div>

              <div className="feature-card">
                <h3>Monitoring</h3>
                <p>
                  Review model performance and
                  degradation.
                </p>
              </div>

              <div className="feature-card">
                <h3>Audit Trail</h3>
                <p>
                  Review important historical model
                  events.
                </p>
              </div>
            </div>
          </section>
        </>
      )}
    </>
  );
}

export default ModelDetail;