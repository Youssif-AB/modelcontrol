import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  Link,
  useParams,
} from "react-router";

import {
  createVersion,
  fetchModel,
  fetchVersions,
} from "../api";

import {
  useAuth,
} from "../auth/useAuth";

import AuditPanel from "../components/AuditPanel";
import FindingsPanel from "../components/FindingsPanel";
import MonitoringPanel from "../components/MonitoringPanel";
import LifecyclePanel from "../components/LifecyclePanel";
import VersionComparison from "../components/VersionComparison";
import MLflowRegistryPanel
  from "../components/MLflowRegistryPanel";

import type {
  MLflowImportResult,
  ModelRecord,
  ModelVersion,
} from "../types";


function ModelDetail() {
  const { modelId } = useParams();

  const { user } = useAuth();

  const parsedModelId = Number(modelId);

  const [model, setModel] =
    useState<ModelRecord | null>(null);

  const [versions, setVersions] =
    useState<ModelVersion[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [actionError, setActionError] =
    useState<string | null>(null);

  const [versionNumber, setVersionNumber] =
    useState(1);

  const [
    versionDescription,
    setVersionDescription,
  ] = useState("");

  const [
    submittingVersion,
    setSubmittingVersion,
  ] = useState(false);

  const [
    auditRefreshToken,
    setAuditRefreshToken,
  ] = useState(0);


  function refreshAudit() {
    setAuditRefreshToken(
      (current) => current + 1,
    );
  }


  useEffect(() => {
    async function loadData() {
      if (
        !modelId ||
        !Number.isInteger(parsedModelId) ||
        parsedModelId <= 0
      ) {
        setError("Invalid model ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const [
          modelData,
          versionData,
        ] = await Promise.all([
          fetchModel(parsedModelId),
          fetchVersions(parsedModelId),
        ]);

        setModel(modelData);
        setVersions(versionData);

        const highestVersion =
          versionData.reduce(
            (highest, version) =>
              Math.max(
                highest,
                version.version_number,
              ),
            0,
          );

        setVersionNumber(
          highestVersion + 1,
        );
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError(
            "Unable to load model.",
          );
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [modelId, parsedModelId]);


  const isAdmin =
    user?.role === "admin";

  const isReviewer =
    user?.role === "reviewer";

  const isOwnerOfModel =
    user?.role === "model_owner" &&
    model !== null &&
    user.email.toLowerCase() ===
      model.owner_email.toLowerCase();

  const canManageModel =
    isAdmin || isOwnerOfModel;

  const canReviewModel =
    isAdmin || isReviewer;

  const canCreateFinding =
    isAdmin || isReviewer;

  const canResolveFinding =
    isAdmin || isOwnerOfModel;

  const canRecordMonitoring =
    isAdmin || isOwnerOfModel;


  async function handleVersionSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setSubmittingVersion(true);
      setActionError(null);

      const created =
        await createVersion(
          parsedModelId,
          {
            version_number:
              versionNumber,

            description:
              versionDescription,
          },
        );

      setVersions((current) => [
        ...current,
        created,
      ]);

      setVersionNumber(
        created.version_number + 1,
      );

      setVersionDescription("");

      refreshAudit();
    } catch (err) {
      if (err instanceof Error) {
        setActionError(err.message);
      } else {
        setActionError(
          "Unable to create version.",
        );
      }
    } finally {
      setSubmittingVersion(false);
    }
  }


  function handleMLflowImported(
    result: MLflowImportResult,
  ) {
    setVersions((current) => [
      ...current,
      result.version,
    ]);

    setVersionNumber(
      result.version.version_number + 1,
    );

    refreshAudit();
  }


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


      {!loading &&
        !error &&
        model && (
          <>
            <header className="detail-header">
              <div>
                <p className="eyebrow">
                  MODEL #{model.id}
                </p>

                <h1>
                  {model.name}
                </h1>

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
                <span>
                  Business Area
                </span>

                <strong>
                  {model.business_area}
                </strong>
              </div>


              <div className="detail-card">
                <span>
                  Model Type
                </span>

                <strong>
                  {model.model_type}
                </strong>
              </div>


              <div className="detail-card">
                <span>
                  Owner
                </span>

                <strong>
                  {model.owner_email}
                </strong>
              </div>


              <div className="detail-card">
                <span>
                  Lifecycle
                </span>

                <strong>
                  {model.lifecycle_status.replace(
                    "_",
                    " ",
                  )}
                </strong>
              </div>
            </section>


            {actionError && (
              <p className="error">
                {actionError}
              </p>
            )}


            <LifecyclePanel
              model={model}
              canManage={canManageModel}
              canReview={canReviewModel}
              onUpdated={(updated) => {
                setModel(updated);
                refreshAudit();
              }}
            />


            <section className="management-grid">
              {canManageModel && (
                <div className="management-card">
                  <div className="section-heading">
                    <div>
                      <h2>
                        Add Version
                      </h2>

                      <p>
                        Register a new version
                        of this model.
                      </p>
                    </div>
                  </div>

                  <form
                    className="version-form"
                    onSubmit={
                      handleVersionSubmit
                    }
                  >
                    <label>
                      Version Number

                      <input
                        type="number"
                        min="1"
                        required
                        value={
                          versionNumber
                        }
                        onChange={(
                          event,
                        ) =>
                          setVersionNumber(
                            Number(
                              event.target
                                .value,
                            ),
                          )
                        }
                      />
                    </label>

                    <label>
                      Description

                      <textarea
                        required
                        minLength={5}
                        value={
                          versionDescription
                        }
                        onChange={(
                          event,
                        ) =>
                          setVersionDescription(
                            event.target
                              .value,
                          )
                        }
                        placeholder="Describe the changes in this version."
                      />
                    </label>

                    <button
                      type="submit"
                      disabled={
                        submittingVersion
                      }
                    >
                      {submittingVersion
                        ? "Adding..."
                        : "Add Version"}
                    </button>
                  </form>
                </div>
              )}


              {!canManageModel && (
                <div className="management-card">
                  <div className="section-heading">
                    <div>
                      <h2>
                        Version Management
                      </h2>

                      <p>
                        Model versions are managed
                        by the model owner.
                      </p>
                    </div>
                  </div>

                  <div className="card-content">
                    <p className="muted-text">
                      Your role has read-only access
                      to version history.
                    </p>
                  </div>
                </div>
              )}
            </section>


            <MLflowRegistryPanel
              modelId={parsedModelId}
              canImport={canManageModel}
              onImported={handleMLflowImported}
            />


            <section className="inventory version-section">
              <div className="section-heading">
                <div>
                  <h2>
                    Model Versions
                  </h2>

                  <p>
                    Version history registered for
                    this model.
                  </p>
                </div>
              </div>

              {versions.length === 0 ? (
                <p className="empty-state">
                  No versions registered yet.
                </p>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>
                          Version
                        </th>

                        <th>
                          Description
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {versions.map(
                        (version) => (
                          <tr
                            key={
                              version.id
                            }
                          >
                            <td>
                              <strong>
                                v
                                {
                                  version.version_number
                                }
                              </strong>
                            </td>

                            <td>
                              {
                                version.description
                              }
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </section>


            <VersionComparison
              model={model}
              versions={versions}
            />


            <FindingsPanel
              modelId={parsedModelId}
              canCreate={canCreateFinding}
              canResolve={canResolveFinding}
              onChanged={refreshAudit}
            />


            <MonitoringPanel
              modelId={parsedModelId}
              canRecord={canRecordMonitoring}
              onChanged={refreshAudit}
            />


            <AuditPanel
              modelId={parsedModelId}
              refreshToken={
                auditRefreshToken
              }
            />
          </>
        )}
    </>
  );
}


export default ModelDetail;
