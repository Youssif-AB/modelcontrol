import { useEffect, useMemo, useState } from "react";

import { fetchMonitoring } from "../api";

import type {
  ModelRecord,
  ModelVersion,
  MonitoringRecord,
} from "../types";


interface VersionComparisonProps {
  model: ModelRecord;
  versions: ModelVersion[];
}


function VersionComparison({
  model,
  versions,
}: VersionComparisonProps) {
  const [monitoring, setMonitoring] =
    useState<MonitoringRecord[]>([]);
  const [leftId, setLeftId] = useState<number | "">("");
  const [rightId, setRightId] = useState<number | "">("");

  useEffect(() => {
    let cancelled = false;

    fetchMonitoring(model.id)
      .then((records) => {
        if (!cancelled) {
          setMonitoring(records);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setMonitoring([]);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [model.id]);

  const left = versions.find((version) => version.id === leftId);
  const right = versions.find((version) => version.id === rightId);

  const metricNames = useMemo(
    () => Array.from(new Set([
      ...Object.keys(left?.metrics ?? {}),
      ...Object.keys(right?.metrics ?? {}),
    ])).sort(),
    [left, right],
  );

  const parameterNames = useMemo(
    () => Array.from(new Set([
      ...Object.keys(left?.params ?? {}),
      ...Object.keys(right?.params ?? {}),
    ])).sort(),
    [left, right],
  );

  const latestMonitoring = monitoring.at(-1);

  if (versions.length < 2) {
    return (
      <section className="comparison-panel">
        <h2>Version comparison</h2>
        <p className="empty-state">
          Add at least two model versions to compare them.
        </p>
      </section>
    );
  }

  return (
    <section className="comparison-panel">
      <div className="section-heading">
        <div>
          <h2>Version comparison</h2>
          <p>
            Compare change descriptions and available MLflow evidence.
          </p>
        </div>
      </div>

      <div className="comparison-selectors">
        <VersionSelect
          label="Baseline version"
          value={leftId}
          versions={versions}
          excludedId={rightId}
          onChange={setLeftId}
        />
        <VersionSelect
          label="Comparison version"
          value={rightId}
          versions={versions}
          excludedId={leftId}
          onChange={setRightId}
        />
      </div>

      {left && right ? (
        <div className="table-wrapper comparison-table">
          <table>
            <thead>
              <tr>
                <th scope="col">Attribute</th>
                <th scope="col">v{left.version_number}</th>
                <th scope="col">v{right.version_number}</th>
              </tr>
            </thead>
            <tbody>
              <ComparisonRow label="Description" left={left.description} right={right.description} />
              <ComparisonRow label="Source" left={left.source_type} right={right.source_type} />
              <ComparisonRow label="MLflow model" left={left.registered_model_name} right={right.registered_model_name} />
              <ComparisonRow label="MLflow version" left={left.external_version} right={right.external_version} />
              <ComparisonRow label="Run ID" left={left.run_id} right={right.run_id} mono />
              <ComparisonRow label="Artifact source" left={left.artifact_source} right={right.artifact_source} mono />
              {metricNames.map((name) => (
                <ComparisonRow
                  key={`metric-${name}`}
                  label={`Metric: ${name}`}
                  left={left.metrics?.[name]}
                  right={right.metrics?.[name]}
                />
              ))}
              {parameterNames.map((name) => (
                <ComparisonRow
                  key={`param-${name}`}
                  label={`Parameter: ${name}`}
                  left={left.params?.[name]}
                  right={right.params?.[name]}
                />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="permission-note">
          Select two different versions to begin the comparison.
        </p>
      )}

      <div className="comparison-context">
        <strong>Current model context</strong>
        <span>{model.risk_tier} risk</span>
        <span>{model.lifecycle_status.replace("_", " ")}</span>
        <span>{model.owner_email}</span>
        <span>
          {latestMonitoring
            ? `Latest monitoring: ${latestMonitoring.status} (${latestMonitoring.metric_name})`
            : "No monitoring records"}
        </span>
      </div>
    </section>
  );
}


interface VersionSelectProps {
  label: string;
  value: number | "";
  versions: ModelVersion[];
  excludedId: number | "";
  onChange: (id: number | "") => void;
}


function VersionSelect({
  label,
  value,
  versions,
  excludedId,
  onChange,
}: VersionSelectProps) {
  return (
    <label>
      {label}
      <select
        value={value}
        onChange={(event) =>
          onChange(event.target.value ? Number(event.target.value) : "")
        }
      >
        <option value="">Select a version</option>
        {versions.map((version) => (
          <option
            disabled={version.id === excludedId}
            key={version.id}
            value={version.id}
          >
            v{version.version_number} · {version.source_type}
          </option>
        ))}
      </select>
    </label>
  );
}


interface ComparisonRowProps {
  label: string;
  left: string | number | null | undefined;
  right: string | number | null | undefined;
  mono?: boolean;
}


function ComparisonRow({
  label,
  left,
  right,
  mono = false,
}: ComparisonRowProps) {
  const leftValue = left ?? "Not available";
  const rightValue = right ?? "Not available";

  return (
    <tr>
      <th scope="row">{label}</th>
      <td className={mono ? "technical-value" : undefined}>{leftValue}</td>
      <td className={mono ? "technical-value" : undefined}>{rightValue}</td>
    </tr>
  );
}


export default VersionComparison;
