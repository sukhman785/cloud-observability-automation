type HealthBadgeProps = {
  status: string;
};

export default function HealthBadge({ status }: HealthBadgeProps) {
  const healthy = status === 'healthy';

  return (
    <div className={`health-badge ${healthy ? 'is-healthy' : 'is-unhealthy'}`}>
      <span className="dot" />
      <span>{healthy ? 'System Healthy' : 'System Unhealthy'}</span>
    </div>
  );
}
