import React, { useEffect, useState } from 'react';
import { usersAPI } from '../api/services';
import type { User } from '../types';

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await usersAPI.getAll();
      setUsers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div style={styles.container}>Loading users...</div>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>👥 User Management</h1>
      <div style={styles.table}>
        <div style={styles.tableHeader}>
          <span>Username</span>
          <span>Email</span>
          <span>Role</span>
          <span>Devices</span>
          <span>Status</span>
        </div>
        {users.map((user) => (
          <div key={user.id} style={styles.tableRow}>
            <span><strong>{user.username}</strong></span>
            <span>{user.email}</span>
            <span>{user.is_staff ? 'Admin' : 'User'}</span>
            <span>{user.device_count}</span>
            <span style={{ color: user.is_active ? '#38ef7d' : '#999' }}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: { padding: '24px', maxWidth: '1400px', margin: '0 auto' },
  title: { fontSize: '32px', marginBottom: '24px' },
  table: { background: 'white', borderRadius: '12px', padding: '20px' },
  tableHeader: { 
    display: 'grid', 
    gridTemplateColumns: 'repeat(5, 1fr)', 
    padding: '12px',
    fontWeight: 'bold',
    borderBottom: '2px solid #eee',
  },
  tableRow: { 
    display: 'grid', 
    gridTemplateColumns: 'repeat(5, 1fr)', 
    padding: '16px 12px',
    borderBottom: '1px solid #eee',
  },
};

export default Users;
