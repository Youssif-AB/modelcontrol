import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  createFinding,
  fetchFindings,
  resolveFinding,
} from "../api";

import type {
  Finding,
  FindingSeverity,
} from "../types";


interface FindingsPanelProps {
  modelId: number;
  canCreate: boolean;
  canResolve: boolean;
  onChanged: () => void;
}


function FindingsPanel({
  modelId,
  canCreate,
  canResolve,
  onChanged,
}: FindingsPanelProps) {
  const [findings, setFindings] =
    useState<Finding[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [title, setTitle] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [severity, setSeverity] =
    useState<FindingSeverity>("medium");

  const [submitting, setSubmitting] =
    useState(false);

  const [resolvingId, setResolvingId] =
    useState<number | null>(null);

  const [
    resolutionNotes,
    setResolutionNotes,
  ] = useState("");


  useEffect(() => {
    let cancelled = false;

    fetchFindings(modelId)
      .then((data) => {
        if (!cancelled) {
          setFindings(data);
          setError(null);
        }
      })
      .catch((err) => {
        if (cancelled) {
          return;
        }

        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError(
            "Unable to load findings.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [modelId]);

  async function handleCreateFinding(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError(null);

      const created =
        await createFinding(
          modelId,
          {
            title,
            description,
            severity,
          },
        );

      setFindings((current) => [
        ...current,
        created,
      ]);

      setTitle("");
      setDescription("");
      setSeverity("medium");

      onChanged();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to create finding.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  async function handleResolve(
    findingId: number,
  ) {
    try {
      setError(null);

      const updated =
        await resolveFinding(
          findingId,
          resolutionNotes,
        );

      setFindings((current) =>
        current.map((finding) =>
          finding.id === findingId
            ? updated
            : finding,
        ),
      );

      setResolvingId(null);
      setResolutionNotes("");

      onChanged();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to resolve finding.",
        );
      }
    }
  }


  const openFindings =
    findings.filter(
      (finding) =>
        finding.status === "open",
    );

  const resolvedFindings =
    findings.filter(
      (finding) =>
        finding.status === "resolved",
    );


  return (
    <section className="panel-section">
      <div className="section-heading">
        <div>
          <h2>
            Review Findings
          </h2>

          <p>
            Record and resolve issues identified
            during model review.
          </p>
        </div>

        <span className="count-badge">
          {openFindings.length} open
        </span>
      </div>


      <div className="panel-content">
        {canCreate && (
          <form
            className="finding-form"
            onSubmit={
              handleCreateFinding
            }
          >
            <h3>
              Add Finding
            </h3>

            <div className="finding-form-grid">
              <label>
                Title

                <input
                  required
                  minLength={3}
                  value={title}
                  onChange={(event) =>
                    setTitle(
                      event.target.value,
                    )
                  }
                  placeholder="Missing validation evidence"
                />
              </label>


              <label>
                Severity

                <select
                  value={severity}
                  onChange={(event) =>
                    setSeverity(
                      event.target
                        .value as FindingSeverity,
                    )
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

                  <option value="critical">
                    Critical
                  </option>
                </select>
              </label>
            </div>


            <label>
              Description

              <textarea
                required
                minLength={10}
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                placeholder="Describe the issue discovered during review."
              />
            </label>


            <button
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? "Adding..."
                : "Add Finding"}
            </button>
          </form>
        )}


        {!canCreate && (
          <p className="permission-note">
            Your role can view findings but
            cannot create new review findings.
          </p>
        )}


        {error && (
          <p className="error">
            {error}
          </p>
        )}


        {loading ? (
          <p className="content-message">
            Loading findings...
          </p>
        ) : (
          <>
            <div className="finding-group">
              <h3>
                Open Findings
              </h3>

              {openFindings.length === 0 ? (
                <p className="muted-text">
                  No open findings.
                </p>
              ) : (
                openFindings.map(
                  (finding) => (
                    <article
                      className="finding-card"
                      key={finding.id}
                    >
                      <div className="finding-header">
                        <div>
                          <h4>
                            {finding.title}
                          </h4>

                          <span
                            className={`severity-badge ${finding.severity}`}
                          >
                            {
                              finding.severity
                            }
                          </span>
                        </div>

                        <span className="status-open">
                          Open
                        </span>
                      </div>


                      <p>
                        {finding.description}
                      </p>


                      {canResolve &&
                        resolvingId ===
                          finding.id && (
                          <div className="resolution-form">
                            <label>
                              Resolution Notes

                              <textarea
                                minLength={5}
                                value={
                                  resolutionNotes
                                }
                                onChange={(
                                  event,
                                ) =>
                                  setResolutionNotes(
                                    event.target
                                      .value,
                                  )
                                }
                                placeholder="Explain how this issue was resolved."
                              />
                            </label>

                            <div className="resolution-actions">
                              <button
                                type="button"
                                disabled={
                                  resolutionNotes
                                    .trim()
                                    .length < 5
                                }
                                onClick={() =>
                                  handleResolve(
                                    finding.id,
                                  )
                                }
                              >
                                Confirm Resolution
                              </button>

                              <button
                                type="button"
                                className="secondary-button"
                                onClick={() => {
                                  setResolvingId(
                                    null,
                                  );

                                  setResolutionNotes(
                                    "",
                                  );
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}


                      {canResolve &&
                        resolvingId !==
                          finding.id && (
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => {
                              setResolvingId(
                                finding.id,
                              );

                              setResolutionNotes(
                                "",
                              );
                            }}
                          >
                            Resolve Finding
                          </button>
                        )}


                      {!canResolve && (
                        <p className="muted-text">
                          Resolution must be completed
                          by the model owner or an
                          administrator.
                        </p>
                      )}
                    </article>
                  ),
                )
              )}
            </div>


            <div className="finding-group">
              <h3>
                Resolved Findings
              </h3>

              {resolvedFindings.length === 0 ? (
                <p className="muted-text">
                  No resolved findings.
                </p>
              ) : (
                resolvedFindings.map(
                  (finding) => (
                    <article
                      className="finding-card resolved"
                      key={finding.id}
                    >
                      <div className="finding-header">
                        <div>
                          <h4>
                            {finding.title}
                          </h4>

                          <span
                            className={`severity-badge ${finding.severity}`}
                          >
                            {
                              finding.severity
                            }
                          </span>
                        </div>

                        <span className="status-resolved">
                          Resolved
                        </span>
                      </div>

                      <p>
                        {finding.description}
                      </p>

                      <div className="resolution-notes">
                        <strong>
                          Resolution
                        </strong>

                        <p>
                          {
                            finding.resolution_notes
                          }
                        </p>
                      </div>
                    </article>
                  ),
                )
              )}
            </div>
          </>
        )}
      </div>
    </section>
  );
}


export default FindingsPanel;