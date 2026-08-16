import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  createMonitoringRecord,
  fetchMonitoring,
} from "../api";

import type {
  MetricDirection,
  MonitoringRecord,
} from "../types";


interface MonitoringPanelProps {
  modelId: number;
  canRecord: boolean;
  onChanged: () => void;
}


function MonitoringPanel({
  modelId,
  canRecord,
  onChanged,
}: MonitoringPanelProps) {
  const [records, setRecords] =
    useState<MonitoringRecord[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [submitting, setSubmitting] =
    useState(false);

  const [metricName, setMetricName] =
    useState("accuracy");

  const [
    baselineValue,
    setBaselineValue,
  ] = useState(0.9);

  const [
    currentValue,
    setCurrentValue,
  ] = useState(0.88);

  const [direction, setDirection] =
    useState<MetricDirection>(
      "higher_is_better",
    );

  const [
    warningThreshold,
    setWarningThreshold,
  ] = useState(0.05);

  const [
    criticalThreshold,
    setCriticalThreshold,
  ] = useState(0.1);


  useEffect(() => {
    let cancelled = false;

    fetchMonitoring(modelId)
      .then((data) => {
        if (!cancelled) {
          setRecords(data);
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
            "Unable to load monitoring records.",
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

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError(null);

      const created =
        await createMonitoringRecord(
          modelId,
          {
            metric_name:
              metricName,

            baseline_value:
              baselineValue,

            current_value:
              currentValue,

            direction,

            warning_threshold:
              warningThreshold,

            critical_threshold:
              criticalThreshold,
          },
        );

      setRecords((current) => [
        ...current,
        created,
      ]);

      onChanged();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to record monitoring metric.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  const latestRecord =
    records.length > 0
      ? records[
          records.length - 1
        ]
      : null;


  const criticalCount =
    records.filter(
      (record) =>
        record.status ===
        "critical",
    ).length;


  const warningCount =
    records.filter(
      (record) =>
        record.status ===
        "warning",
    ).length;


  function formatPercentage(
    value: number,
  ) {
    return `${(
      value * 100
    ).toFixed(1)}%`;
  }


  return (
    <section className="panel-section">
      <div className="section-heading">
        <div>
          <h2>
            Performance Monitoring
          </h2>

          <p>
            Compare current model metrics with
            baseline performance and identify
            degradation.
          </p>
        </div>

        {latestRecord && (
          <span
            className={`monitoring-status ${latestRecord.status}`}
          >
            {latestRecord.status}
          </span>
        )}
      </div>


      <div className="panel-content">
        <div className="monitoring-summary">
          <div className="monitoring-summary-card">
            <span>
              Total Checks
            </span>

            <strong>
              {records.length}
            </strong>
          </div>


          <div className="monitoring-summary-card">
            <span>
              Warnings
            </span>

            <strong>
              {warningCount}
            </strong>
          </div>


          <div className="monitoring-summary-card">
            <span>
              Critical
            </span>

            <strong>
              {criticalCount}
            </strong>
          </div>


          <div className="monitoring-summary-card">
            <span>
              Latest Status
            </span>

            <strong>
              {latestRecord
                ? latestRecord.status
                : "No data"}
            </strong>
          </div>
        </div>


        {canRecord && (
          <form
            className="monitoring-form"
            onSubmit={handleSubmit}
          >
            <h3>
              Record Performance Metric
            </h3>

            <div className="monitoring-form-grid">
              <label>
                Metric Name

                <input
                  required
                  minLength={2}
                  value={metricName}
                  onChange={(event) =>
                    setMetricName(
                      event.target.value,
                    )
                  }
                  placeholder="accuracy"
                />
              </label>


              <label>
                Direction

                <select
                  value={direction}
                  onChange={(event) =>
                    setDirection(
                      event.target
                        .value as MetricDirection,
                    )
                  }
                >
                  <option value="higher_is_better">
                    Higher is better
                  </option>

                  <option value="lower_is_better">
                    Lower is better
                  </option>
                </select>
              </label>


              <label>
                Baseline Value

                <input
                  required
                  type="number"
                  min="0.000001"
                  step="any"
                  value={baselineValue}
                  onChange={(event) =>
                    setBaselineValue(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                />
              </label>


              <label>
                Current Value

                <input
                  required
                  type="number"
                  min="0"
                  step="any"
                  value={currentValue}
                  onChange={(event) =>
                    setCurrentValue(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                />
              </label>


              <label>
                Warning Threshold

                <input
                  required
                  type="number"
                  min="0.001"
                  step="0.01"
                  value={warningThreshold}
                  onChange={(event) =>
                    setWarningThreshold(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                />
              </label>


              <label>
                Critical Threshold

                <input
                  required
                  type="number"
                  min="0.001"
                  step="0.01"
                  value={criticalThreshold}
                  onChange={(event) =>
                    setCriticalThreshold(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                />
              </label>
            </div>


            <button
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? "Recording..."
                : "Record Metric"}
            </button>
          </form>
        )}


        {!canRecord && (
          <p className="permission-note">
            Your role has read-only access to
            performance monitoring.
          </p>
        )}


        {error && (
          <p className="error">
            {error}
          </p>
        )}


        <div className="monitoring-history">
          <h3>
            Monitoring History
          </h3>

          {loading ? (
            <p className="content-message">
              Loading monitoring data...
            </p>
          ) : records.length === 0 ? (
            <p className="muted-text">
              No monitoring records yet.
            </p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>
                      Metric
                    </th>

                    <th>
                      Baseline
                    </th>

                    <th>
                      Current
                    </th>

                    <th>
                      Degradation
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Recorded
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {[...records]
                    .reverse()
                    .map(
                      (record) => (
                        <tr
                          key={
                            record.id
                          }
                        >
                          <td>
                            <strong>
                              {
                                record.metric_name
                              }
                            </strong>

                            <span className="metric-direction">
                              {record.direction ===
                              "higher_is_better"
                                ? "Higher is better"
                                : "Lower is better"}
                            </span>
                          </td>

                          <td>
                            {
                              record.baseline_value
                            }
                          </td>

                          <td>
                            {
                              record.current_value
                            }
                          </td>

                          <td>
                            {formatPercentage(
                              record.degradation,
                            )}
                          </td>

                          <td>
                            <span
                              className={`monitoring-status ${record.status}`}
                            >
                              {
                                record.status
                              }
                            </span>
                          </td>

                          <td>
                            {new Date(
                              record.created_at,
                            ).toLocaleString()}
                          </td>
                        </tr>
                      ),
                    )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


export default MonitoringPanel;