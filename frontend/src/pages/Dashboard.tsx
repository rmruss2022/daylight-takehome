import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { devicesAPI } from '../api/services';
import { DeviceStats, Device } from '../types';
import DeviceList from '../components/DeviceList';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DeviceStats | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      console.log('[Dashboard] Starting to load data...');
      
      const [statsData, devicesData] = await Promise.all([
        devicesAPI.getStats(),
        devicesAPI.getAll(),
      ]);
      
      console.log('[Dashboard] Stats data received:', statsData);
      console.log('[Dashboard] Stats is truthy?', !!statsData);
      console.log('[Dashboard] Devices data received:', devicesData);
      console.log('[Dashboard] Devices count:', devicesData.length);
      
      setStats(statsData);
      setDevices(devicesData);
      
      console.log('[Dashboard] State updated. Stats:', statsData);
    } catch (err: any) {
      setError('Failed to load dashboard data');
      console.error('[Dashboard] Load error:', err);
      console.error('[Dashboard] Error details:', err.response?.data || err.message);
    } finally {
      setLoading(false);
      console.log('[Dashboard] Loading complete');
    }
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <p style={styles.errorText}>{error}</p>
        <button onClick={loadData} style={styles.retryButton}>Retry</button>
      </div>
    );
  }

  // Debug: Log current state at render time
  console.log('[Dashboard] Rendering. Stats:', stats, 'Devices:', devices.length);

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Dashboard</h1>
          <p style={styles.subtitle}>
            Welcome back, {user?.first_name || user?.username}!
          </p>
        </div>
      </div>

      {stats ? (
        <div style={styles.statsGrid}>
          <div style={{ ...styles.statCard, ...styles.statTotal }}>
            <div style={styles.statIcon}>📊</div>
            <div>
              <div style={styles.statValue}>{stats.total}</div>
              <div style={styles.statLabel}>Total Devices</div>
            </div>
          </div>
          
          <div style={{ ...styles.statCard, ...styles.statOnline }}>
            <div style={styles.statIcon}>✅</div>
            <div>
              <div style={styles.statValue}>{stats.online}</div>
              <div style={styles.statLabel}>Online</div>
            </div>
          </div>
          
          <div style={{ ...styles.statCard, ...styles.statOffline }}>
            <div style={styles.statIcon}>⭕</div>
            <div>
              <div style={styles.statValue}>{stats.offline}</div>
              <div style={styles.statLabel}>Offline</div>
            </div>
          </div>
          
          <div style={{ ...styles.statCard, ...styles.statError }}>
            <div style={styles.statIcon}>⚠️</div>
            <div>
              <div style={styles.statValue}>{stats.error}</div>
              <div style={styles.statLabel}>Errors</div>
            </div>
          </div>
        </div>
      ) : (
        <div style={{ padding: '20px', background: '#fff3cd', borderRadius: '8px', marginBottom: '20px' }}>
          <p style={{ color: '#856404', margin: 0 }}>
            ⚠️ Stats data not available. Check browser console for errors.
          </p>
        </div>
      )}

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Recent Devices</h2>
        <DeviceList devices={devices} onRefresh={loadData} />
      </div>
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
    marginBottom: '32px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '32px',
  },
  statCard: {
    padding: '24px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  statTotal: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
  },
  statOnline: {
    background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    color: 'white',
  },
  statOffline: {
    background: 'linear-gradient(135deg, #757F9A 0%, #D7DDE8 100%)',
    color: 'white',
  },
  statError: {
    background: 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
    color: 'white',
  },
  statIcon: {
    fontSize: '36px',
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '4px',
  },
  statLabel: {
    fontSize: '14px',
    opacity: 0.9,
  },
  section: {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '20px',
    color: '#1a1a1a',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    gap: '16px',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    gap: '16px',
  },
  errorText: {
    color: '#c33',
    fontSize: '16px',
  },
  retryButton: {
    padding: '10px 24px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
  },
};

export default Dashboard;
