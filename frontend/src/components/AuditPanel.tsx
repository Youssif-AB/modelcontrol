import { useEffect, useMemo, useState } from "react";

import { fetchAudit } from "../api";
import type { AuditEvent } from "../types";

interface AuditPanelProps {
  modelId: number;
  refreshToken: number;
}

function formatEventLabel(eventType: string): string {
  return eventType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function AuditPanel({ modelId, refreshToken }: AuditPanelProps) {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [eventType, setEventType] = useState("all");
  const [newestFirst, setNewestFirst] = useState(true);
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetchAudit(modelId)
      .then((data) => {
        if (!cancelled) setEvents(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load audit history.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [modelId, refreshToken, retryToken]);

  const eventTypes = useMemo(
    () => Array.from(new Set(events.map((event) => event.event_type))).sort(),
    [events],
  );

  const filteredEvents = useMemo(() => {
    const query = search.trim().toLowerCase();
    const matching = events.filter((event) => {
      const searchable = [
        event.description,
        event.event_type,
        event.actor_email ?? "",
      ].join(" ").toLowerCase();

      return (
        (eventType === "all" || event.event_type === eventType) &&
        (!query || searchable.includes(query))
      );
    });

    return newestFirst ? [...matching].reverse() : matching;
  }, [eventType, events, newestFirst, search]);

  return (
    <section className="panel-section audit-panel">
      <div className="section-heading">
        <div>
          <h2>Audit trail</h2>
          <p>Immutable history of governance actions for this model.</p>
        </div>
        <span className="count-badge">{events.length} events</span>
      </div>

      <div className="panel-content">
        {loading && <p className="content-message" role="status">Loading audit history...</p>}

        {error && (
          <div className="error-state" role="alert">
            <p className="error">{error}</p>
            <button className="secondary-button" type="button" onClick={() => {
              setLoading(true);
              setError(null);
              setRetryToken((value) => value + 1);
            }}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <p className="empty-state">No audit events recorded.</p>
        )}

        {!loading && !error && events.length > 0 && (
          <>
            <div className="audit-controls">
              <label>
                Search history
                <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search action, actor, or reason" />
              </label>
              <label>
                Event type
                <select value={eventType} onChange={(event) => setEventType(event.target.value)}>
                  <option value="all">All event types</option>
                  {eventTypes.map((type) => <option key={type} value={type}>{formatEventLabel(type)}</option>)}
                </select>
              </label>
              <label>
                Order
                <select value={newestFirst ? "newest" : "oldest"} onChange={(event) => setNewestFirst(event.target.value === "newest")}>
                  <option value="newest">Newest first</option>
                  <option value="oldest">Oldest first</option>
                </select>
              </label>
            </div>

            {filteredEvents.length === 0 ? (
              <p className="empty-state">No audit events match the current filters.</p>
            ) : (
              <ol className="audit-timeline">
                {filteredEvents.map((event) => (
                  <li className="audit-event" key={event.id}>
                    <div className="audit-body">
                      <div className="audit-event-header">
                        <strong>{formatEventLabel(event.event_type)}</strong>
                        <time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString()}</time>
                      </div>
                      <p>{event.description}</p>
                      <span className="audit-actor">
                        {event.actor_email ? `Actor: ${event.actor_email}` : "Actor not recorded"}
                      </span>
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </>
        )}
      </div>
    </section>
  );
}

export default AuditPanel;
