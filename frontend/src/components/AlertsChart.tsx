import type { Summary } from '../services/api';

type AlertsChartProps = {
  points: Summary['alerts_over_time'];
};

export default function AlertsChart({ points }: AlertsChartProps) {
  const max = Math.max(...points.map((point) => point.count), 1);

  return (
    <section className="panel reveal-5">
      <h3>Alerts Over Time</h3>
      <p className="chart-subtitle">Alerts per minute (last 20 minutes)</p>
      <div className="chart">
        {points.length === 0 ? <p className="empty">No alerts yet.</p> : null}
        {points.map((point) => {
          const height = `${Math.max(10, (point.count / max) * 100)}%`;
          const label = point.timestamp.slice(11, 16);
          return (
            <div className="bar-item" key={point.timestamp} title={`${point.timestamp}: ${point.count}`}>
              <span className="bar-count">{point.count}</span>
              <div className="bar" style={{ height }} />
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
