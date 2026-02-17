import React, { useEffect, useState } from 'react';
import { batteriesAPI } from '../api/services';
import type { Battery } from '../types';

const Batteries: React.FC = () => {
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadBatteries();
  }, []);

  const loadBatteries = async () => {
    try {
      setLoading(true);
      const data = await batteriesAPI.getAll();
      setBatteries(data);
    } catch (err: any) {
      setError('Failed to load batteries');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#38ef7d';
      case 'offline':
        return '#999';
      case 'error':
        return '#f45c43';
      default:
        return '#666';
    }
  };

  const getChargeColor = (percentage: number) => {
    if (percentage >= 70) return '#38ef7d';
    if (percentage >= 30) return '#ffa500';
    return '#f45c43';
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading batteries...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>{error}</div>
        <button onClick={loadBatteries} style={styles.retryButton}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>🔋 Battery Management</h1>
          <p style={styles.subtitle}>
            Monitor and manage all battery devices
          </p>
        </div>
        <button onClick={loadBatteries} style={styles.refreshButton}>
          🔄 Refresh
        </button>
      </div>

      {batteries.length === 0 ? (
        <div style={styles.emptyState}>
          <p>No batteries found</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {batteries.map((battery) => (
            <div key={battery.id} style={styles.card}>
              <div style={styles.cardHeader}>
                <h3 style={styles.cardTitle}>{battery.name}</h3>
                <span
                  style={{
                    ...styles.statusBadge,
                    backgroundColor: getStatusColor(battery.status),
                  }}
                >
                  {battery.status}
                </span>
              </div>

              <div style={styles.cardBody}>
                <div style={styles.chargeSection}>
                  <div style={styles.chargeLabel}>
                    <span>Charge Level</span>
                    <span style={{ fontWeight: 'bold' }}>
                      {battery.charge_percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div style={styles.progressBar}>
                    <div
                      style={{
                        ...styles.progressFill,
                        width: `${battery.charge_percentage}%`,
                        backgroundColor: getChargeColor(battery.charge_percentage),
                      }}
                    />
                  </div>
                  <div style={styles.chargeDetails}>
                    {battery.current_charge_kwh.toFixed(2)} kWh /{' '}
                    {battery.capacity_kwh.toFixed(2)} kWh
                  </div>
                </div>

                <div style={styles.specs}>
                  <div style={styles.specItem}>
                    <span style={styles.specLabel}>Capacity</span>
                    <span style={styles.specValue}>
                      {battery.capacity_kwh} kWh
                    </span>
                  </div>
                  <div style={styles.specItem}>
                    <span style={styles.specLabel}>Max Charge Rate</span>
                    <span style={styles.specValue}>
                      {battery.max_charge_rate_kw} kW
                    </span>
                  </div>
                  <div style={styles.specItem}>
                    <span style={styles.specLabel}>Max Discharge Rate</span>
                    <span style={styles.specValue}>
                      {battery.max_discharge_rate_kw} kW
                    </span>
                  </div>
                  <div style={styles.specItem}>
                    <span style={styles.specLabel}>Owner</span>
                    <span style={styles.specValue}>
                      {battery.user_username}
                    </span>
                  </div>
                </div>
              </div>

              <div style={styles.cardFooter}>
                <span style={styles.timestamp}>
                  Updated: {new Date(battery.updated_at).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: '24px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1a1a1a',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
    margin: 0,
  },
  refreshButton: {
    padding: '10px 20px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '24px',
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    overflow: 'hidden',
  },
  cardHeader: {
    padding: '20px',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardTitle: {
    fontSize: '20px',
    fontWeight: '600',
    margin: 0,
    color: '#1a1a1a',
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '12px',
    color: 'white',
    fontSize: '12px',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  cardBody: {
    padding: '20px',
  },
  chargeSection: {
    marginBottom: '24px',
  },
  chargeLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
    fontSize: '14px',
    color: '#666',
  },
  progressBar: {
    height: '12px',
    background: '#eee',
    borderRadius: '6px',
    overflow: 'hidden',
    marginBottom: '8px',
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease',
  },
  chargeDetails: {
    fontSize: '13px',
    color: '#999',
  },
  specs: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  specItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '14px',
  },
  specLabel: {
    color: '#666',
  },
  specValue: {
    fontWeight: '600',
    color: '#333',
  },
  cardFooter: {
    padding: '16px 20px',
    background: '#f9f9f9',
    borderTop: '1px solid #eee',
  },
  timestamp: {
    fontSize: '12px',
    color: '#999',
  },
  loading: {
    textAlign: 'center',
    padding: '48px',
    fontSize: '16px',
    color: '#666',
  },
  error: {
    textAlign: 'center',
    padding: '48px',
    fontSize: '16px',
    color: '#c33',
  },
  retryButton: {
    display: 'block',
    margin: '16px auto',
    padding: '10px 24px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  emptyState: {
    textAlign: 'center',
    padding: '48px',
    fontSize: '16px',
    color: '#666',
  },
};

export default Batteries;
