import type { Alert } from '../services/api';

type AlertTableProps = {
  alerts: Alert[];
  onAcknowledge: (alert: Alert) => void;
  onSuppress: (alert: Alert) => void;
  busyAlertId: string | null;
};

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString();
}

export default function AlertTable({ alerts, onAcknowledge, onSuppress, busyAlertId }: AlertTableProps) {
  return (
    <section className="panel reveal-4">
      <h3>Alert Feed</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Type</th>
              <th>Service</th>
              <th>Status</th>
              <th>Timestamp</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => {
              const key = alert.alert_id ?? `${alert.id}`;
              const isBusy = busyAlertId !== null && busyAlertId === alert.alert_id;
              const canAcknowledge = alert.status === 'OPEN' && !!alert.alert_id;
              const canSuppress = alert.status !== 'SUPPRESSED' && !!alert.alert_id;

              return (
                <tr key={key}>
                  <td>
                    <span className={`severity severity-${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                  </td>
                  <td>{alert.alert_type}</td>
                  <td>{alert.source_service}</td>
                  <td>
                    <span className={`status-pill status-${alert.status.toLowerCase()}`}>{alert.status}</span>
                  </td>
                  <td>{formatTime(alert.timestamp)}</td>
                  <td className="actions-cell">
                    <button
                      className="action-button"
                      disabled={!canAcknowledge || isBusy}
                      onClick={() => onAcknowledge(alert)}
                    >
                      Ack
                    </button>
                    <button
                      className="action-button muted"
                      disabled={!canSuppress || isBusy}
                      onClick={() => onSuppress(alert)}
                    >
                      Suppress
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
