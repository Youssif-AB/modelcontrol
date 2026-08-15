import {
  useEffect,
  useState,
} from "react";

import { fetchAudit } from "../api";
import type { AuditEvent } from "../types";


interface AuditPanelProps {
  modelId: number;
  refreshToken: number;
}


function AuditPanel({
  modelId,
  refreshToken,
}: AuditPanelProps) {
  const [events, setEvents] =
    useState<AuditEvent[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    async function loadAudit() {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchAudit(modelId);

        setEvents(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError(
            "Unable to load audit history.",
          );
        }
      } finally {
        setLoading(false);
      }
    }

    loadAudit();
  }, [modelId, refreshToken]);


  return (
    <section className="panel-section">
      <div className="section-heading">
        <div>
          <h2>Audit Trail</h2>

          <p>
            Historical record of important actions
            affecting this model.
          </p>
        </div>
      </div>

      <div className="panel-content">
        {loading && (
          <p className="content-message">
            Loading audit history...
          </p>
        )}

        {error && (
          <p className="error">
            {error}
          </p>
        )}

        {!loading &&
          !error &&
          events.length === 0 && (
            <p className="muted-text">
              No audit events recorded.
            </p>
          )}

        {!loading &&
          !error &&
          events.length > 0 && (
            <div className="audit-timeline">
              {[...events]
                .reverse()
                .map((event) => (
                  <div
                    className="audit-event"
                    key={event.id}
                  >
                    <div className="audit-dot" />

                    <div className="audit-body">
                      <div className="audit-event-header">
                        <strong>
                          {event.event_type
                            .replaceAll("_", " ")}
                        </strong>

                        <time>
                          {new Date(
                            event.created_at,
                          ).toLocaleString()}
                        </time>
                      </div>

                      <p>
                        {event.description}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          )}
      </div>
    </section>
  );
}


export default AuditPanel;