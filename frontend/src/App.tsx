import { useEffect, useMemo, useRef, useState } from 'react';
import AlertTable from './components/AlertTable';
import AlertsChart from './components/AlertsChart';
import HealthBadge from './components/HealthBadge';
import SummaryCards from './components/SummaryCards';
import {
  acknowledgeAlert,
  fetchAlerts,
  fetchHealth,
  fetchSummary,
  getAlertsWsUrl,
  suppressAlert,
  type Alert,
  type Summary
} from './services/api';

const EMPTY_SUMMARY: Summary = {
  total_alerts: 0,
  critical_alerts: 0,
  open_alerts: 0,
  acknowledged_alerts: 0,
  suppressed_alerts: 0,
  top_service_by_alerts: { service: null, count: 0 },
  alerts_over_time: []
};

const MAX_ALERTS = 100;

function mergeAlerts(current: Alert[], incoming: Alert[]): Alert[] {
  const byId = new Map<number, Alert>();

  for (const alert of [...incoming, ...current]) {
    byId.set(alert.id, alert);
  }

  return [...byId.values()].sort((a, b) => b.id - a.id).slice(0, MAX_ALERTS);
}

export default function App() {
  const [status, setStatus] = useState('unknown');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<Summary>(EMPTY_SUMMARY);
  const [error, setError] = useState<string | null>(null);
  const [busyAlertId, setBusyAlertId] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<number | null>(null);

  useEffect(() => {
    let active = true;

    const loadStatic = async () => {
      try {
        const [health, summaryResult] = await Promise.all([fetchHealth(), fetchSummary()]);
        if (!active) {
          return;
        }
        setStatus(health.status);
        setSummary(summaryResult);
      } catch {
        if (active) {
          setStatus('unhealthy');
          setError('Unable to reach API at http://localhost:8000');
        }
      }
    };

    const connectWs = () => {
      const socket = new WebSocket(getAlertsWsUrl());
      socketRef.current = socket;

      socket.onopen = () => {
        if (active) {
          setError(null);
        }
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as { type: 'snapshot' | 'delta'; items: Alert[] };
          setAlerts((current) => mergeAlerts(current, payload.items));
        } catch {
          // Ignore invalid frame.
        }
      };

      socket.onerror = () => {
        if (active) {
          setError('WebSocket connection failed. Retrying...');
        }
      };

      socket.onclose = () => {
        if (!active) {
          return;
        }
        reconnectRef.current = window.setTimeout(connectWs, 2000);
      };
    };

    const bootstrap = async () => {
      try {
        const alertsResult = await fetchAlerts(MAX_ALERTS);
        if (!active) {
          return;
        }
        setAlerts(alertsResult.items);
        await loadStatic();
        connectWs();
      } catch {
        if (active) {
          setError('Unable to reach API at http://localhost:8000');
        }
      }
    };

    bootstrap();
    const summaryTimer = window.setInterval(loadStatic, 10000);

    return () => {
      active = false;
      window.clearInterval(summaryTimer);
      if (reconnectRef.current) {
        window.clearTimeout(reconnectRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const latestTimestamp = useMemo(() => alerts[0]?.timestamp, [alerts]);

  const applyAlertUpdate = (nextItem: Alert) => {
    setAlerts((current) => current.map((item) => (item.id === nextItem.id ? nextItem : item)));
    fetchSummary().then(setSummary).catch(() => undefined);
  };

  const onAcknowledge = async (alert: Alert) => {
    if (!alert.alert_id) {
      return;
    }
    try {
      setBusyAlertId(alert.alert_id);
      const result = await acknowledgeAlert(alert.alert_id);
      applyAlertUpdate(result.item);
    } catch {
      setError(`Failed to acknowledge ${alert.alert_id}`);
    } finally {
      setBusyAlertId(null);
    }
  };

  const onSuppress = async (alert: Alert) => {
    if (!alert.alert_id) {
      return;
    }
    try {
      setBusyAlertId(alert.alert_id);
      const result = await suppressAlert(alert.alert_id);
      applyAlertUpdate(result.item);
    } catch {
      setError(`Failed to suppress ${alert.alert_id}`);
    } finally {
      setBusyAlertId(null);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero reveal-1">
        <div>
          <p className="kicker">Cloud Observability</p>
          <h1>Automated Response Dashboard</h1>
          <p className="subtitle">
            Live operational view of generated incidents, severity distribution, and service impact.
          </p>
        </div>
        <div className="status-stack">
          <HealthBadge status={status} />
          <small>Latest alert: {latestTimestamp ? new Date(latestTimestamp).toLocaleString() : 'N/A'}</small>
        </div>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      <SummaryCards summary={summary} />

      <section className="two-col">
        <AlertsChart points={summary.alerts_over_time} />
        <AlertTable
          alerts={alerts}
          onAcknowledge={onAcknowledge}
          onSuppress={onSuppress}
          busyAlertId={busyAlertId}
        />
      </section>
    </main>
  );
}
