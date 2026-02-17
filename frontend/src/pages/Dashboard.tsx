import React, { useEffect, useMemo, useState } from 'react';
import { dashboardAPI } from '../api/services';
import type { EnergyStats, GraphQLDevice } from '../types';

const REFRESH_MS = 5000;

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<EnergyStats | null>(null);
  const [devices, setDevices] = useState<GraphQLDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('--:--:--');

  const fetchDashboardData = async (isInitial = false) => {
    try {
      if (isInitial) setLoading(true);
      const result = await dashboardAPI.getEnergyAndDevices();
      setStats(result.energyStats);
      setDevices(result.allDevices || []);
      setError('');
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err?.message || 'Failed to load dashboard data');
    } finally {
      if (isInitial) setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(true);
    const id = window.setInterval(() => fetchDashboardData(false), REFRESH_MS);
    return () => window.clearInterval(id);
  }, []);

  const flowSummary = useMemo(() => {
    if (!stats) {
      return {
        gridLabel: 'Balanced',
        gridIcon: '⚖️',
        solarProduction: 0,
        generatorProduction: 0,
        hvacConsumption: 0,
        batteryFlow: 0,
        evFlow: 0,
      };
    }

    return {
      gridLabel:
        stats.netGridFlow > 100
          ? 'Drawing from Grid'
          : stats.netGridFlow < -100
            ? 'Sending to Grid'
            : 'Balanced',
      gridIcon: stats.netGridFlow > 100 ? '⬆️' : stats.netGridFlow < -100 ? '⬇️' : '⚖️',
      solarProduction: Math.round(stats.currentProduction * 0.7),
      generatorProduction: Math.round(stats.currentProduction * 0.3),
      hvacConsumption: Math.round(stats.currentConsumption * 0.6),
      batteryFlow: Math.round(stats.currentStorageFlow * 0.6),
      evFlow: Math.round(stats.currentStorageFlow * 0.4),
    };
  }, [stats]);

  if (loading) {
    return <div style={styles.center}>Loading energy dashboard...</div>;
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Energy Dashboard</h1>
          <div style={styles.subtitle}>Live Data • Last updated: {lastUpdated}</div>
        </div>
        <button style={styles.refreshButton} onClick={() => fetchDashboardData(false)}>
          Refresh
        </button>
      </header>

      {error ? <div style={styles.error}>{error}</div> : null}

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Energy Overview</h2>
        <div style={styles.statsGrid}>
          <StatCard label="Total Production" value={Math.round(stats?.currentProduction || 0)} unit="W" />
          <StatCard label="Total Consumption" value={Math.round(stats?.currentConsumption || 0)} unit="W" />
          <StatCard
            label="Storage Level"
            value={(stats?.currentStorage?.percentage || 0).toFixed(1)}
            unit="%"
            subtitle={`${((stats?.currentStorage?.currentLevelWh || 0) / 1000).toFixed(1)} kWh / ${((stats?.currentStorage?.totalCapacityWh || 0) / 1000).toFixed(1)} kWh`}
          />
          <StatCard
            label="Net Grid Flow"
            value={Math.round(Math.abs(stats?.netGridFlow || 0))}
            unit="W"
            subtitle={`${flowSummary.gridIcon} ${flowSummary.gridLabel}`}
          />
        </div>
      </section>

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Energy Flow</h2>
        <div style={styles.flowGrid}>
          <FlowItem icon="☀️" label="Solar Panels" value={flowSummary.solarProduction} />
          <FlowItem icon="⚙️" label="Generators" value={flowSummary.generatorProduction} />
          <FlowItem icon="❄️" label="HVAC Systems" value={flowSummary.hvacConsumption} />
          <FlowItem icon="🔋" label="Battery Storage" value={flowSummary.batteryFlow} />
          <FlowItem icon="🚗" label="Electric Vehicles" value={flowSummary.evFlow} />
          <FlowItem icon="🏠" label="Net Flow" value={Math.round(stats?.netGridFlow || 0)} />
        </div>
      </section>

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Connected Devices</h2>
        {devices.length === 0 ? (
          <div style={styles.empty}>No devices connected</div>
        ) : (
          <div style={styles.deviceGrid}>
            {devices.map((device) => (
              <article key={`${device.__typename}-${device.id}`} style={styles.deviceCard}>
                <div style={styles.deviceHeader}>
                  <h3 style={styles.deviceTitle}>{device.name}</h3>
                  <span style={styles.deviceType}>{formatType(device.__typename)}</span>
                </div>
                <div style={styles.deviceMeta}>
                  <span style={statusBadgeStyle(device.status)}>{formatStatus(device)}</span>
                </div>
                <div style={styles.deviceSpecs}>
                  {getDeviceSpecs(device).map((spec) => (
                    <div key={spec.label} style={styles.specRow}>
                      <span style={styles.specLabel}>{spec.label}</span>
                      <span style={styles.specValue}>{spec.value}</span>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: number | string; unit: string; subtitle?: string }> = ({
  label,
  value,
  unit,
  subtitle,
}) => (
  <div style={styles.statCard}>
    <div style={styles.statLabel}>{label}</div>
    <div style={styles.statValue}>
      {value} <span style={styles.statUnit}>{unit}</span>
    </div>
    {subtitle ? <div style={styles.statSubtitle}>{subtitle}</div> : null}
  </div>
);

const FlowItem: React.FC<{ icon: string; label: string; value: number }> = ({ icon, label, value }) => (
  <div style={styles.flowItem}>
    <div style={styles.flowIcon}>{icon}</div>
    <div>
      <div style={styles.flowLabel}>{label}</div>
      <div style={styles.flowValue}>{value} W</div>
    </div>
  </div>
);

function formatType(typeName: string): string {
  return typeName.replace('Type', '').replace(/([A-Z])/g, ' $1').trim();
}

function formatStatus(device: GraphQLDevice): string {
  if (device.mode) {
    const mode = device.mode.toUpperCase();
    if (mode === 'CHARGING') return 'Charging';
    if (mode === 'DISCHARGING') return 'Discharging';
    return 'Disconnected';
  }
  return device.status === 'ONLINE' ? 'Online' : 'Offline';
}

function statusBadgeStyle(status: string): React.CSSProperties {
  const online = status === 'ONLINE' || status === 'CHARGING' || status === 'DISCHARGING';
  return {
    ...styles.badge,
    background: online ? 'rgba(0, 255, 136, 0.15)' : 'rgba(148, 163, 184, 0.18)',
    color: online ? '#00ff88' : '#94a3b8',
    borderColor: online ? 'rgba(0, 255, 136, 0.35)' : 'rgba(148, 163, 184, 0.35)',
  };
}

function getDeviceSpecs(device: GraphQLDevice): Array<{ label: string; value: string }> {
  const specs: Array<{ label: string; value: string }> = [];
  if (device.maxCapacityW !== undefined) specs.push({ label: 'Max Output', value: `${Math.round(device.maxCapacityW)} W` });
  if (device.ratedOutputW !== undefined) specs.push({ label: 'Rated Output', value: `${Math.round(device.ratedOutputW)} W` });
  if (device.ratedPowerW !== undefined) specs.push({ label: 'Rated Power', value: `${Math.round(device.ratedPowerW)} W` });
  if (device.capacityKwh !== undefined) specs.push({ label: 'Capacity', value: `${device.capacityKwh.toFixed(1)} kWh` });
  if (device.currentChargeKwh !== undefined) specs.push({ label: 'Current Charge', value: `${device.currentChargeKwh.toFixed(1)} kWh` });
  if (device.chargePercentage !== undefined) specs.push({ label: 'Charge Level', value: `${device.chargePercentage.toFixed(1)}%` });
  if (device.efficiency !== undefined) specs.push({ label: 'Efficiency', value: `${(device.efficiency * 100).toFixed(1)}%` });
  return specs;
}

const styles: Record<string, React.CSSProperties> = {
  container: { padding: 24, maxWidth: 1400, margin: '0 auto' },
  center: { minHeight: 400, display: 'grid', placeItems: 'center', color: '#64748b' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { margin: 0, color: '#0f172a' },
  subtitle: { marginTop: 6, color: '#64748b' },
  refreshButton: {
    border: '1px solid #cbd5e1',
    borderRadius: 8,
    padding: '8px 14px',
    background: '#fff',
    cursor: 'pointer',
  },
  error: { marginBottom: 16, padding: 12, borderRadius: 8, background: '#fee2e2', color: '#991b1b' },
  section: { background: '#fff', borderRadius: 12, padding: 20, marginBottom: 18, border: '1px solid #e2e8f0' },
  sectionTitle: { marginTop: 0, marginBottom: 14, color: '#0f172a' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 },
  statCard: { border: '1px solid #e2e8f0', borderRadius: 10, padding: 14 },
  statLabel: { color: '#64748b', fontSize: 13, marginBottom: 8 },
  statValue: { color: '#0f172a', fontSize: 30, fontWeight: 700, lineHeight: 1.2 },
  statUnit: { color: '#64748b', fontSize: 16, fontWeight: 500 },
  statSubtitle: { marginTop: 8, color: '#64748b', fontSize: 13 },
  flowGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 },
  flowItem: { display: 'flex', alignItems: 'center', gap: 12, border: '1px solid #e2e8f0', borderRadius: 10, padding: 12 },
  flowIcon: { fontSize: 24 },
  flowLabel: { color: '#64748b', fontSize: 13 },
  flowValue: { color: '#0f172a', fontWeight: 700, marginTop: 2 },
  empty: { padding: 24, color: '#64748b' },
  deviceGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 },
  deviceCard: { border: '1px solid #e2e8f0', borderRadius: 10, padding: 14, background: '#fff' },
  deviceHeader: { display: 'flex', justifyContent: 'space-between', gap: 10, marginBottom: 8 },
  deviceTitle: { margin: 0, color: '#0f172a', fontSize: 18 },
  deviceType: { color: '#64748b', fontSize: 12, marginTop: 3 },
  deviceMeta: { marginBottom: 10 },
  badge: {
    border: '1px solid transparent',
    borderRadius: 999,
    padding: '4px 10px',
    fontSize: 12,
    fontWeight: 700,
    textTransform: 'uppercase',
    display: 'inline-block',
  },
  deviceSpecs: { display: 'grid', gap: 6 },
  specRow: { display: 'flex', justifyContent: 'space-between', gap: 12 },
  specLabel: { color: '#64748b', fontSize: 13 },
  specValue: { color: '#0f172a', fontSize: 13, fontWeight: 600 },
};

export default Dashboard;
