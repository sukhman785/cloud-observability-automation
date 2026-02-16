import type { Summary } from '../services/api';

type SummaryCardsProps = {
  summary: Summary;
};

export default function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <section className="summary-grid">
      <article className="summary-card reveal-1">
        <p>Total Alerts</p>
        <h2>{summary.total_alerts}</h2>
      </article>
      <article className="summary-card reveal-2">
        <p>Critical Alerts</p>
        <h2>{summary.critical_alerts}</h2>
      </article>
      <article className="summary-card reveal-3">
        <p>Open</p>
        <h2>{summary.open_alerts}</h2>
      </article>
      <article className="summary-card reveal-3">
        <p>Acknowledged</p>
        <h2>{summary.acknowledged_alerts}</h2>
      </article>
      <article className="summary-card reveal-3">
        <p>Suppressed</p>
        <h2>{summary.suppressed_alerts}</h2>
      </article>
      <article className="summary-card reveal-3">
        <p>Top Service by Alerts</p>
        <h2>{summary.top_service_by_alerts.service ?? 'N/A'}</h2>
        <small>{summary.top_service_by_alerts.count} alerts</small>
      </article>
    </section>
  );
}
