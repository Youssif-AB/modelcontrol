import {
  useEffect,
  useState,
} from "react";

import {
  fetchMLflowModels,
  importMLflowVersion,
} from "../api";

import type {
  MLflowImportResult,
  MLflowRegisteredModel,
  MLflowVersionSummary,
} from "../types";


interface MLflowRegistryPanelProps {
  modelId: number;
  canImport: boolean;
  onImported: (
    result: MLflowImportResult,
  ) => void;
}


interface SelectedVersion {
  model: MLflowRegisteredModel;
  version: MLflowVersionSummary;
}


function MLflowRegistryPanel({
  modelId,
  canImport,
  onImported,
}: MLflowRegistryPanelProps) {
  const [models, setModels] =
    useState<MLflowRegisteredModel[]>([]);

  const [selected, setSelected] =
    useState<SelectedVersion | null>(null);

  const [lastImport, setLastImport] =
    useState<MLflowImportResult | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [importing, setImporting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    let cancelled = false;

    fetchMLflowModels()
      .then((data) => {
        if (!cancelled) {
          setModels(data);
          setError(null);
        }
      })
      .catch((err) => {
        if (cancelled) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load the MLflow registry.",
        );
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);


  async function handleImport() {
    if (!selected) {
      return;
    }

    try {
      setImporting(true);
      setError(null);

      const result =
        await importMLflowVersion(
          modelId,
          {
            model_name: selected.model.name,
            version: selected.version.version,
          },
        );

      setLastImport(result);
      onImported(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to import the MLflow version.",
      );
    } finally {
      setImporting(false);
    }
  }


  return (
    <section className="panel-section mlflow-panel">
      <div className="section-heading">
        <div>
          <h2>MLflow Registry</h2>

          <p>
            Browse registered models, inspect run
            provenance, and import a governed version.
          </p>
        </div>

        <span className="count-badge">
          {models.length} registered
        </span>
      </div>

      <div className="panel-content">
        {!canImport && (
          <p className="permission-note">
            You have read-only access to the MLflow
            registry. Imports are limited to this
            model&apos;s owner and administrators.
          </p>
        )}

        {loading && (
          <p className="content-message">
            Loading MLflow registry...
          </p>
        )}

        {error && (
          <p className="error">{error}</p>
        )}

        {!loading &&
          models.length === 0 &&
          !error && (
            <p className="empty-state">
              No registered MLflow models were found.
            </p>
          )}

        {!loading && models.length > 0 && (
          <div className="mlflow-browser">
            <div className="mlflow-model-list">
              {models.map((registeredModel) => (
                <article
                  className="mlflow-model"
                  key={registeredModel.name}
                >
                  <div className="mlflow-model-heading">
                    <div>
                      <h3>{registeredModel.name}</h3>

                      <p>
                        {registeredModel.description ||
                          "No model description provided."}
                      </p>
                    </div>

                    <span className="count-badge">
                      {registeredModel.versions.length}
                      {" "}
                      {registeredModel.versions.length === 1
                        ? "version"
                        : "versions"}
                    </span>
                  </div>

                  {registeredModel.versions.length === 0 ? (
                    <p className="muted-text">
                      No versions registered.
                    </p>
                  ) : (
                    <div className="mlflow-version-list">
                      {registeredModel.versions.map(
                        (version) => {
                          const isSelected =
                            selected?.model.name ===
                              registeredModel.name &&
                            selected.version.version ===
                              version.version;

                          return (
                            <button
                              className={`mlflow-version-button${
                                isSelected ? " selected" : ""
                              }`}
                              key={version.version}
                              type="button"
                              aria-pressed={isSelected}
                              onClick={() =>
                                setSelected({
                                  model: registeredModel,
                                  version,
                                })
                              }
                            >
                              <span>
                                Version {version.version}
                              </span>

                              <small>
                                {version.status ||
                                  "Status unavailable"}
                              </small>
                            </button>
                          );
                        },
                      )}
                    </div>
                  )}
                </article>
              ))}
            </div>

            <aside className="mlflow-provenance">
              <h3>Run Provenance</h3>

              {!selected ? (
                <p className="muted-text">
                  Select a model version to inspect its
                  MLflow provenance.
                </p>
              ) : (
                <>
                  <dl className="provenance-list">
                    <div>
                      <dt>Registered Model</dt>
                      <dd>{selected.model.name}</dd>
                    </div>

                    <div>
                      <dt>MLflow Version</dt>
                      <dd>{selected.version.version}</dd>
                    </div>

                    <div>
                      <dt>Status</dt>
                      <dd>
                        {selected.version.status || "Unavailable"}
                      </dd>
                    </div>

                    <div>
                      <dt>Run ID</dt>
                      <dd>
                        {selected.version.run_id || "Unavailable"}
                      </dd>
                    </div>

                    <div>
                      <dt>Artifact Source</dt>
                      <dd>
                        {selected.version.source || "Unavailable"}
                      </dd>
                    </div>
                  </dl>

                  {canImport && (
                    <button
                      type="button"
                      disabled={importing}
                      onClick={handleImport}
                    >
                      {importing
                        ? "Importing..."
                        : "Import into ModelControl"}
                    </button>
                  )}
                </>
              )}

              {lastImport && (
                <div className="mlflow-import-result">
                  <h3>
                    Imported as v
                    {lastImport.version.version_number}
                  </h3>

                  <ProvenanceValues
                    title="Run Metrics"
                    values={lastImport.mlflow.metrics}
                  />

                  <ProvenanceValues
                    title="Run Parameters"
                    values={lastImport.mlflow.params}
                  />
                </div>
              )}
            </aside>
          </div>
        )}
      </div>
    </section>
  );
}


interface ProvenanceValuesProps {
  title: string;
  values: Record<string, number | string>;
}


function ProvenanceValues({
  title,
  values,
}: ProvenanceValuesProps) {
  const entries = Object.entries(values);

  return (
    <div className="provenance-values">
      <h4>{title}</h4>

      {entries.length === 0 ? (
        <p className="muted-text">
          None recorded.
        </p>
      ) : (
        <dl>
          {entries.map(([key, value]) => (
            <div key={key}>
              <dt>{key}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  );
}


export default MLflowRegistryPanel;
