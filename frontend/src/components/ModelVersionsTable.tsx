import type {
  ModelVersion,
} from "../types";


interface ModelVersionsTableProps {
  versions: ModelVersion[];
}


const legacyMLflowDescription =
  /^Imported from MLflow\.\s*registered_model=([^;]+);\s*mlflow_version=([^;]+);/;


function formatVersionDescription(
  version: ModelVersion,
): string {
  const legacyMatch = version.description.match(
    legacyMLflowDescription,
  );

  if (
    version.source_type !== "mlflow"
    && !legacyMatch
  ) {
    return version.description;
  }

  const modelName =
    version.registered_model_name
    || legacyMatch?.[1]?.trim();

  const externalVersion =
    version.external_version
    || legacyMatch?.[2]?.trim();

  if (modelName && externalVersion) {
    return (
      `Imported from MLflow — ${modelName} `
      + `v${externalVersion}`
    );
  }

  return "Imported from MLflow";
}


function ModelVersionsTable({
  versions,
}: ModelVersionsTableProps) {
  if (versions.length === 0) {
    return (
      <p className="empty-state">
        No versions registered yet.
      </p>
    );
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Version</th>
            <th>Description</th>
            <th>Source</th>
            <th>Created</th>
          </tr>
        </thead>

        <tbody>
          {versions.map((version) => (
            <tr key={version.id}>
              <td>
                <strong>
                  v{version.version_number}
                </strong>
              </td>

              <td>
                {formatVersionDescription(version)}
              </td>

              <td>
                <span className="badge">
                  {version.source_type}
                </span>
              </td>

              <td>
                {new Date(
                  version.created_at,
                ).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


export default ModelVersionsTable;
