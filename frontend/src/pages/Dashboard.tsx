import {
  useEffect,
  useState,
} from "react";

import { Link } from "react-router";

import { fetchModels } from "../api";
import type { ModelRecord } from "../types";


function Dashboard() {
  const [models, setModels] = useState<ModelRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadModels() {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchModels();

      setModels(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to load model inventory.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadModels();
  }, []);

  const highRiskModels = models.filter(
    (model) => model.risk_tier === "high",
  ).length;

  const underReviewModels = models.filter(
    (model) => model.lifecycle_status === "under_review",
  ).length;

  const approvedModels = models.filter(
    (model) => model.lifecycle_status === "approved",
  ).length;

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">
            MODEL GOVERNANCE PLATFORM
          </p>

          <h1>ModelControl</h1>

          <p className="subtitle">
            Track model ownership, risk, lifecycle,
            and governance activity.
          </p>
        </div>

        <div className="header-actions">
          <button
            className="secondary-button"
            onClick={loadModels}
          >
            Refresh
          </button>

          <Link
            className="button-link"
            to="/models/new"
          >
            Register Model
          </Link>
        </div>
      </header>

      <section className="summary-grid">
        <div className="summary-card">
          <span>Total Models</span>
          <strong>{models.length}</strong>
        </div>

        <div className="summary-card">
          <span>High Risk</span>
          <strong>{highRiskModels}</strong>
        </div>

        <div className="summary-card">
          <span>Under Review</span>
          <strong>{underReviewModels}</strong>
        </div>

        <div className="summary-card">
          <span>Approved</span>
          <strong>{approvedModels}</strong>
        </div>
      </section>

      <section className="inventory">
        <div className="section-heading">
          <div>
            <h2>Model Inventory</h2>
            <p>
              Registered models across the organization.
            </p>
          </div>
        </div>

        {loading && (
          <p className="content-message">
            Loading models...
          </p>
        )}

        {error && (
          <p className="error">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Model</th>
                  <th>Business Area</th>
                  <th>Type</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Owner</th>
                </tr>
              </thead>

              <tbody>
                {models.map((model) => (
                  <tr key={model.id}>
                    <td>{model.id}</td>

                    <td>
                      <Link
                        className="model-link"
                        to={`/models/${model.id}`}
                      >
                        {model.name}
                      </Link>

                      <span className="purpose">
                        {model.purpose}
                      </span>
                    </td>

                    <td>{model.business_area}</td>

                    <td>
                      {model.model_type}
                    </td>

                    <td>
                      <span
                        className={`badge ${model.risk_tier}`}
                      >
                        {model.risk_tier}
                      </span>
                    </td>

                    <td>
                      <span className="badge">
                        {model.lifecycle_status.replace(
                          "_",
                          " ",
                        )}
                      </span>
                    </td>

                    <td>{model.owner_email}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {models.length === 0 && (
              <p className="empty-state">
                No models registered yet.
              </p>
            )}
          </div>
        )}
      </section>
    </>
  );
}

export default Dashboard;