export type Alert = {
  id: number;
  alert_id: string | null;
  timestamp: string;
  alert_generated_at: string | null;
  alert_type: string;
  severity: string;
  description: string;
  source_service: string;
  source_trace_id: string | null;
  offending_ip: string | null;
  status: 'OPEN' | 'ACKNOWLEDGED' | 'SUPPRESSED';
  acknowledged_at: string | null;
  suppressed_at: string | null;
  updated_at: string;
};

export type Summary = {
  total_alerts: number;
  critical_alerts: number;
  open_alerts: number;
  acknowledged_alerts: number;
  suppressed_alerts: number;
  top_service_by_alerts: {
    service: string | null;
    count: number;
  };
  alerts_over_time: Array<{
    timestamp: string;
    count: number;
  }>;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function post<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST'
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchHealth(): Promise<{ status: string }> {
  return get<{ status: string }>('/health');
}

export function fetchAlerts(limit = 100): Promise<{ items: Alert[] }> {
  return get<{ items: Alert[] }>(`/alerts?limit=${limit}`);
}

export function fetchSummary(): Promise<Summary> {
  return get<Summary>('/metrics/summary');
}

export function acknowledgeAlert(alertId: string): Promise<{ item: Alert }> {
  return post<{ item: Alert }>(`/alerts/${alertId}/acknowledge`);
}

export function suppressAlert(alertId: string): Promise<{ item: Alert }> {
  return post<{ item: Alert }>(`/alerts/${alertId}/suppress`);
}

export function getAlertsWsUrl(): string {
  const parsed = new URL(API_BASE);
  parsed.protocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:';
  parsed.pathname = '/ws/alerts';
  return parsed.toString();
}
