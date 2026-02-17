import React from 'react';
import type { Device } from '../types';
import { useNavigate } from 'react-router-dom';

interface DeviceListProps {
  devices: Device[];
  onRefresh: () => void;
}

const DeviceList: React.FC<DeviceListProps> = ({ devices, onRefresh }) => {
  const navigate = useNavigate();

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

  const getDeviceIcon = (deviceType: string) => {
    const icons: { [key: string]: string } = {
      battery: '🔋',
      electric_vehicle: '🚗',
      solar_panel: '☀️',
      generator: '⚡',
      air_conditioner: '❄️',
      heater: '🔥',
    };
    return icons[deviceType] || '📱';
  };

  const handleDeviceClick = (device: Device) => {
    const typeMap: { [key: string]: string } = {
      battery: 'batteries',
      electric_vehicle: 'electric-vehicles',
      solar_panel: 'solar-panels',
      generator: 'generators',
      air_conditioner: 'air-conditioners',
      heater: 'heaters',
    };
    const path = typeMap[device.device_type];
    if (path) {
      navigate(`/${path}`);
    }
  };

  if (devices.length === 0) {
    return (
      <div style={styles.emptyState}>
        <p style={styles.emptyText}>No devices found</p>
        <button onClick={onRefresh} style={styles.refreshButton}>
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div style={styles.tableHeader}>
        <button onClick={onRefresh} style={styles.refreshButton}>
          🔄 Refresh
        </button>
      </div>
      <div style={styles.table}>
        <div style={styles.tableRow}>
          <div style={styles.tableHeaderCell}>Type</div>
          <div style={styles.tableHeaderCell}>Name</div>
          <div style={styles.tableHeaderCell}>Owner</div>
          <div style={styles.tableHeaderCell}>Status</div>
          <div style={styles.tableHeaderCell}>Created</div>
        </div>
        {devices.map((device) => (
          <div
            key={device.id}
            style={styles.tableRow}
            onClick={() => handleDeviceClick(device)}
          >
            <div style={styles.tableCell}>
              <span style={styles.deviceIcon}>
                {getDeviceIcon(device.device_type)}
              </span>
              {device.device_type.replace('_', ' ')}
            </div>
            <div style={styles.tableCell}>
              <strong>{device.name}</strong>
            </div>
            <div style={styles.tableCell}>{device.user_username}</div>
            <div style={styles.tableCell}>
              <span
                style={{
                  ...styles.statusBadge,
                  backgroundColor: getStatusColor(device.status),
                }}
              >
                {device.status}
              </span>
            </div>
            <div style={styles.tableCell}>
              {new Date(device.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  table: {
    width: '100%',
  },
  tableHeader: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '16px',
  },
  tableRow: {
    display: 'grid',
    gridTemplateColumns: '200px 1fr 150px 120px 150px',
    padding: '16px',
    borderBottom: '1px solid #eee',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  tableHeaderCell: {
    fontWeight: '600',
    color: '#666',
    fontSize: '14px',
    textTransform: 'uppercase',
  },
  tableCell: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '15px',
    color: '#333',
  },
  deviceIcon: {
    marginRight: '8px',
    fontSize: '20px',
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '12px',
    color: 'white',
    fontSize: '12px',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  emptyState: {
    textAlign: 'center',
    padding: '48px',
  },
  emptyText: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '16px',
  },
  refreshButton: {
    padding: '8px 16px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
  },
};

export default DeviceList;
