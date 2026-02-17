import React, { useEffect, useState } from 'react';
import { usersAPI } from '../api/services';
import type { User, UserWritePayload } from '../types';
import { useAuth } from '../context/AuthContext';

const Users: React.FC = () => {
  const { user: currentUser } = useAuth();
  const isStaff = Boolean(currentUser?.is_staff);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [forbidden, setForbidden] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [saving, setSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
  });
  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirmPassword: '',
    is_active: true,
    is_staff: false,
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError('');
      setForbidden(false);
      if (currentUser?.is_staff) {
        const data = await usersAPI.getAll();
        setUsers(data);
        return;
      }

      setForbidden(true);
      const me = await usersAPI.getMe();
      setUsers([me]);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const openEdit = (user: User) => {
    setEditingUser(user);
    setEditForm({
      username: user.username,
      email: user.email || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      is_active: user.is_active,
      is_staff: user.is_staff,
    });
    setShowEdit(true);
  };

  const openCreate = () => {
    setCreateForm({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      confirmPassword: '',
      is_active: true,
      is_staff: false,
    });
    setShowCreate(true);
  };

  const saveEdit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editingUser || !currentUser?.is_staff) return;
    try {
      setSaving(true);
      await usersAPI.update(editingUser.id, editForm);
      setShowEdit(false);
      setEditingUser(null);
      await loadUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to update user');
    } finally {
      setSaving(false);
    }
  };

  const deleteUser = async (user: User) => {
    if (!currentUser?.is_staff) return;
    if (user.id === currentUser.id) {
      setError('You cannot delete your currently logged-in admin account.');
      return;
    }
    const ok = window.confirm(`Delete user "${user.username}"?`);
    if (!ok) return;
    try {
      await usersAPI.delete(user.id);
      await loadUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to delete user');
    }
  };

  const createUser = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!currentUser?.is_staff) return;
    if (createForm.password !== createForm.confirmPassword) {
      setError('Password and confirm password must match.');
      return;
    }
    try {
      setSaving(true);
      const payload: UserWritePayload = {
        username: createForm.username.trim(),
        email: createForm.email.trim(),
        first_name: createForm.first_name.trim(),
        last_name: createForm.last_name.trim(),
        password: createForm.password,
        is_active: createForm.is_active,
        is_staff: createForm.is_staff,
      };
      await usersAPI.create(payload);
      setShowCreate(false);
      await loadUsers();
    } catch (err: any) {
      const detail = err?.response?.data;
      const firstError =
        (detail && typeof detail === 'object' && Object.values(detail)[0]) ||
        err?.response?.data?.detail;
      setError(String(firstError || err?.message || 'Failed to create user'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div style={styles.container}>Loading users...</div>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>👥 User Management</h1>
      {forbidden ? (
        <div style={styles.notice}>You do not have admin permissions. Showing your account only.</div>
      ) : null}
      {error ? (
        <div style={styles.errorWrap}>
          <div>{error}</div>
          <button onClick={loadUsers} style={styles.retryButton}>Retry</button>
        </div>
      ) : null}
      {isStaff ? (
        <div style={styles.toolbar}>
          <button style={styles.addButton} onClick={openCreate}>Add User</button>
        </div>
      ) : null}
      <div style={styles.table}>
        <div style={{ ...styles.tableHeader, gridTemplateColumns: isStaff ? '1.1fr 1.4fr 0.8fr 0.6fr 0.7fr 0.9fr' : '1.2fr 1.6fr 1fr 0.8fr 0.8fr' }}>
          <span>Username</span>
          <span>Email</span>
          <span>Role</span>
          <span>Devices</span>
          <span>Status</span>
          {isStaff ? <span>Actions</span> : null}
        </div>
        {users.map((user) => (
          <div key={user.id} style={{ ...styles.tableRow, gridTemplateColumns: isStaff ? '1.1fr 1.4fr 0.8fr 0.6fr 0.7fr 0.9fr' : '1.2fr 1.6fr 1fr 0.8fr 0.8fr' }}>
            <span><strong>{user.username}</strong></span>
            <span>{user.email}</span>
            <span>{user.is_staff ? 'Admin' : user.id === currentUser?.id ? 'You' : 'User'}</span>
            <span>{user.device_count}</span>
            <span style={{ color: user.is_active ? '#38ef7d' : '#999' }}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
            {isStaff ? (
              <span style={styles.actionsCell}>
                <button style={styles.editButton} onClick={() => openEdit(user)}>Edit</button>
                <button style={styles.deleteButton} onClick={() => deleteUser(user)}>Delete</button>
              </span>
            ) : null}
          </div>
        ))}
      </div>

      {showEdit && editingUser ? (
        <div style={styles.modalBackdrop}>
          <form style={styles.modalCard} onSubmit={saveEdit}>
            <h3 style={styles.modalTitle}>Edit User: {editingUser.username}</h3>
            <div style={styles.formGrid}>
              <label style={styles.formField}>
                <span>Username</span>
                <input
                  value={editForm.username}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, username: e.target.value }))}
                  required
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Email</span>
                <input
                  value={editForm.email}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, email: e.target.value }))}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>First name</span>
                <input
                  value={editForm.first_name}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, first_name: e.target.value }))}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Last name</span>
                <input
                  value={editForm.last_name}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, last_name: e.target.value }))}
                  style={styles.input}
                />
              </label>
            </div>
            <div style={styles.checkboxRow}>
              <label>
                <input
                  type="checkbox"
                  checked={editForm.is_active}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                />{' '}
                Active
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={editForm.is_staff}
                  onChange={(e) => setEditForm((prev) => ({ ...prev, is_staff: e.target.checked }))}
                />{' '}
                Admin
              </label>
            </div>
            <div style={styles.modalActions}>
              <button
                type="button"
                style={styles.cancelButton}
                onClick={() => {
                  setShowEdit(false);
                  setEditingUser(null);
                }}
                disabled={saving}
              >
                Cancel
              </button>
              <button type="submit" style={styles.saveButton} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
      {showCreate ? (
        <div style={styles.modalBackdrop}>
          <form style={styles.modalCard} onSubmit={createUser}>
            <h3 style={styles.modalTitle}>Add User</h3>
            <div style={styles.formGrid}>
              <label style={styles.formField}>
                <span>Username</span>
                <input
                  value={createForm.username}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, username: e.target.value }))}
                  required
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Email</span>
                <input
                  value={createForm.email}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, email: e.target.value }))}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>First name</span>
                <input
                  value={createForm.first_name}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, first_name: e.target.value }))}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Last name</span>
                <input
                  value={createForm.last_name}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, last_name: e.target.value }))}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Password</span>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, password: e.target.value }))}
                  required
                  minLength={8}
                  style={styles.input}
                />
              </label>
              <label style={styles.formField}>
                <span>Confirm password</span>
                <input
                  type="password"
                  value={createForm.confirmPassword}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                  required
                  minLength={8}
                  style={styles.input}
                />
              </label>
            </div>
            <div style={styles.checkboxRow}>
              <label>
                <input
                  type="checkbox"
                  checked={createForm.is_active}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                />{' '}
                Active
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={createForm.is_staff}
                  onChange={(e) => setCreateForm((prev) => ({ ...prev, is_staff: e.target.checked }))}
                />{' '}
                Admin
              </label>
            </div>
            <div style={styles.modalActions}>
              <button type="button" style={styles.cancelButton} onClick={() => setShowCreate(false)} disabled={saving}>
                Cancel
              </button>
              <button type="submit" style={styles.saveButton} disabled={saving}>
                {saving ? 'Saving...' : 'Create User'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: { padding: '24px', maxWidth: '1400px', margin: '0 auto' },
  title: { fontSize: '32px', marginBottom: '24px' },
  notice: {
    marginBottom: '12px',
    padding: '10px 12px',
    background: '#eef2ff',
    color: '#3730a3',
    borderRadius: '8px',
  },
  errorWrap: {
    marginBottom: '12px',
    padding: '10px 12px',
    background: '#fef2f2',
    color: '#991b1b',
    borderRadius: '8px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '10px',
  },
  retryButton: {
    border: 'none',
    borderRadius: '6px',
    padding: '6px 10px',
    background: '#dc2626',
    color: 'white',
    cursor: 'pointer',
    fontWeight: 600,
  },
  table: { background: 'white', borderRadius: '12px', padding: '20px' },
  toolbar: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '12px',
  },
  addButton: {
    border: '1px solid #16a34a',
    background: '#16a34a',
    color: 'white',
    borderRadius: '8px',
    padding: '8px 12px',
    cursor: 'pointer',
    fontWeight: 700,
  },
  tableHeader: { 
    display: 'grid', 
    padding: '12px',
    fontWeight: 'bold',
    borderBottom: '2px solid #eee',
  },
  tableRow: { 
    display: 'grid', 
    padding: '16px 12px',
    borderBottom: '1px solid #eee',
    alignItems: 'center',
  },
  actionsCell: { display: 'flex', gap: '8px' },
  editButton: {
    border: '1px solid #cbd5e1',
    background: 'white',
    borderRadius: '6px',
    padding: '5px 8px',
    cursor: 'pointer',
  },
  deleteButton: {
    border: '1px solid #dc2626',
    background: '#dc2626',
    color: 'white',
    borderRadius: '6px',
    padding: '5px 8px',
    cursor: 'pointer',
  },
  modalBackdrop: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(15,23,42,0.55)',
    display: 'grid',
    placeItems: 'center',
    zIndex: 9999,
    padding: '16px',
  },
  modalCard: {
    width: '100%',
    maxWidth: '680px',
    background: 'white',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid #e2e8f0',
  },
  modalTitle: { marginTop: 0, marginBottom: '12px' },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
  },
  formField: {
    display: 'grid',
    gap: '6px',
    fontSize: '13px',
    color: '#475569',
  },
  input: {
    border: '1px solid #cbd5e1',
    borderRadius: '8px',
    padding: '8px 10px',
  },
  checkboxRow: {
    marginTop: '12px',
    display: 'flex',
    gap: '14px',
  },
  modalActions: {
    marginTop: '14px',
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '8px',
  },
  cancelButton: {
    border: '1px solid #cbd5e1',
    background: 'white',
    borderRadius: '8px',
    padding: '8px 12px',
    cursor: 'pointer',
  },
  saveButton: {
    border: '1px solid #16a34a',
    background: '#16a34a',
    color: 'white',
    borderRadius: '8px',
    padding: '8px 12px',
    cursor: 'pointer',
    fontWeight: 700,
  },
};

export default Users;
