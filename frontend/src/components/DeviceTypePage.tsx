import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';

type DeviceRecord = Record<string, any>;

export interface FieldConfig {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'select';
  required?: boolean;
  options?: Array<{ label: string; value: string | number }>;
  step?: string;
  min?: number;
  placeholder?: string;
  defaultValue?: string | number;
  formatter?: (value: any, row: DeviceRecord) => string;
}

interface DeviceTypePageProps {
  title: string;
  subtitle: string;
  emptyMessage: string;
  fetchItems: () => Promise<DeviceRecord[]>;
  fields: FieldConfig[];
  formFields?: FieldConfig[];
  createItem?: (payload: DeviceRecord) => Promise<any>;
  updateItem?: (id: number, payload: DeviceRecord) => Promise<any>;
  deleteItem?: (id: number) => Promise<void>;
}

const DeviceTypePage: React.FC<DeviceTypePageProps> = ({
  title,
  subtitle,
  emptyMessage,
  fetchItems,
  fields,
  formFields = [],
  createItem,
  updateItem,
  deleteItem,
}) => {
  const { user } = useAuth();
  const isStaff = Boolean(user?.is_staff);

  const [items, setItems] = useState<DeviceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<DeviceRecord | null>(null);
  const [formValues, setFormValues] = useState<DeviceRecord>({});

  const loadItems = async () => {
    try {
      setLoading(true);
      const data = await fetchItems();
      setItems(data);
      setError('');
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => {
      const nameA = String(a.name || '').toLowerCase();
      const nameB = String(b.name || '').toLowerCase();
      return nameA.localeCompare(nameB);
    });
  }, [items]);

  const resetForm = () => {
    const defaults: DeviceRecord = {};
    for (const field of formFields) {
      defaults[field.key] = field.defaultValue ?? '';
    }
    if (defaults.status === undefined) {
      defaults.status = 'online';
    }
    setFormValues(defaults);
  };

  const openCreateForm = () => {
    setEditingItem(null);
    resetForm();
    setShowForm(true);
  };

  const openEditForm = (item: DeviceRecord) => {
    const values: DeviceRecord = {};
    for (const field of formFields) {
      values[field.key] = item[field.key] ?? '';
    }
    setEditingItem(item);
    setFormValues(values);
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingItem(null);
    setFormValues({});
  };

  const buildPayload = (): DeviceRecord => {
    const payload: DeviceRecord = {};
    for (const field of formFields) {
      const raw = formValues[field.key];
      if (field.type === 'number') {
        payload[field.key] = raw === '' || raw === null || raw === undefined ? null : Number(raw);
      } else {
        payload[field.key] = raw;
      }
    }
    return payload;
  };

  const onSubmitForm = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!isStaff) return;
    try {
      setSubmitting(true);
      const payload = buildPayload();
      if (editingItem && updateItem) {
        await updateItem(Number(editingItem.id), payload);
      } else if (createItem) {
        await createItem(payload);
      }
      closeForm();
      await loadItems();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to save changes');
    } finally {
      setSubmitting(false);
    }
  };

  const onDeleteItem = async (item: DeviceRecord) => {
    if (!isStaff || !deleteItem) return;
    const ok = window.confirm(`Delete "${item.name}"? This cannot be undone.`);
    if (!ok) return;
    try {
      await deleteItem(Number(item.id));
      await loadItems();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to delete item');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>{title}</h1>
          <p style={styles.subtitle}>{subtitle}</p>
        </div>
        <div style={styles.headerActions}>
          <button onClick={loadItems} style={styles.refreshButton}>
            Refresh
          </button>
          {isStaff && createItem && formFields.length > 0 ? (
            <button onClick={openCreateForm} style={styles.addButton}>
              Add
            </button>
          ) : null}
        </div>
      </div>

      {error ? (
        <div style={styles.errorWrap}>
          <p style={styles.errorText}>{error}</p>
          <button onClick={loadItems} style={styles.retryButton}>
            Retry
          </button>
        </div>
      ) : null}

      {loading ? (
        <div style={styles.centerText}>Loading...</div>
      ) : sortedItems.length === 0 ? (
        <div style={styles.centerText}>{emptyMessage}</div>
      ) : (
        <div style={styles.grid}>
          {sortedItems.map((item) => (
            <article key={String(item.id)} style={styles.card}>
              <div style={styles.cardHeader}>
                <div>
                  <h3 style={styles.cardTitle}>{item.name}</h3>
                  <div style={styles.owner}>Owner: {item.user_username || 'Unknown'}</div>
                </div>
                <span style={statusStyle(item.status)}>{String(item.status || '').toUpperCase()}</span>
              </div>

              <div style={styles.fieldList}>
                {fields.map((field) => {
                  const raw = item[field.key];
                  const value = field.formatter
                    ? field.formatter(raw, item)
                    : raw !== undefined && raw !== null
                      ? String(raw)
                      : '-';
                  return (
                    <div key={field.key} style={styles.fieldRow}>
                      <span style={styles.fieldLabel}>{field.label}</span>
                      <span style={styles.fieldValue}>{value}</span>
                    </div>
                  );
                })}
              </div>

              {isStaff ? (
                <div style={styles.cardActions}>
                  {updateItem && formFields.length > 0 ? (
                    <button style={styles.secondaryActionButton} onClick={() => openEditForm(item)}>
                      Edit
                    </button>
                  ) : null}
                  {deleteItem ? (
                    <button style={styles.dangerActionButton} onClick={() => onDeleteItem(item)}>
                      Delete
                    </button>
                  ) : null}
                </div>
              ) : null}

              <div style={styles.updatedAt}>
                Updated: {item.updated_at ? new Date(item.updated_at).toLocaleString() : '-'}
              </div>
            </article>
          ))}
        </div>
      )}

      {showForm ? (
        <div style={styles.modalBackdrop}>
          <form style={styles.modalCard} onSubmit={onSubmitForm}>
            <h3 style={styles.modalTitle}>{editingItem ? `Edit ${editingItem.name}` : `Add ${title.replace(/^[^A-Za-z]+/, '')}`}</h3>
            <div style={styles.modalFields}>
              {formFields.map((field) => (
                <label key={field.key} style={styles.fieldBlock}>
                  <span style={styles.fieldCaption}>{field.label}</span>
                  {field.type === 'select' ? (
                    <select
                      value={formValues[field.key] ?? ''}
                      onChange={(e) => setFormValues((prev) => ({ ...prev, [field.key]: e.target.value }))}
                      required={field.required}
                      style={styles.input}
                    >
                      {(field.options || []).map((option) => (
                        <option key={String(option.value)} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type || 'text'}
                      value={formValues[field.key] ?? ''}
                      onChange={(e) => setFormValues((prev) => ({ ...prev, [field.key]: e.target.value }))}
                      required={field.required}
                      step={field.step}
                      min={field.min}
                      placeholder={field.placeholder}
                      style={styles.input}
                    />
                  )}
                </label>
              ))}
            </div>
            <div style={styles.modalActions}>
              <button type="button" style={styles.secondaryActionButton} onClick={closeForm} disabled={submitting}>
                Cancel
              </button>
              <button type="submit" style={styles.addButton} disabled={submitting}>
                {submitting ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  );
};

function statusStyle(status: string | undefined): React.CSSProperties {
  if (status === 'online') {
    return { ...styles.badge, backgroundColor: '#dcfce7', color: '#166534' };
  }
  if (status === 'error') {
    return { ...styles.badge, backgroundColor: '#fee2e2', color: '#991b1b' };
  }
  return { ...styles.badge, backgroundColor: '#e2e8f0', color: '#334155' };
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: 24,
    maxWidth: 1400,
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    gap: 16,
  },
  headerActions: {
    display: 'flex',
    gap: 8,
  },
  title: {
    margin: 0,
    fontSize: 32,
    color: '#0f172a',
  },
  subtitle: {
    margin: '8px 0 0 0',
    color: '#64748b',
    fontSize: 15,
  },
  refreshButton: {
    border: '1px solid #cbd5e1',
    background: 'white',
    borderRadius: 8,
    padding: '10px 16px',
    cursor: 'pointer',
    fontWeight: 600,
  },
  addButton: {
    border: '1px solid #16a34a',
    background: '#16a34a',
    color: 'white',
    borderRadius: 8,
    padding: '10px 16px',
    cursor: 'pointer',
    fontWeight: 700,
  },
  centerText: {
    background: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: 12,
    padding: 28,
    textAlign: 'center',
    color: '#64748b',
  },
  errorWrap: {
    marginBottom: 16,
    padding: 14,
    borderRadius: 10,
    background: '#fff1f2',
    border: '1px solid #fecdd3',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  errorText: {
    margin: 0,
    color: '#9f1239',
  },
  retryButton: {
    border: 'none',
    background: '#e11d48',
    color: 'white',
    borderRadius: 8,
    padding: '8px 12px',
    cursor: 'pointer',
    fontWeight: 600,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: 14,
  },
  card: {
    background: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: 12,
    padding: 14,
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
  },
  cardTitle: {
    margin: 0,
    color: '#0f172a',
    fontSize: 19,
  },
  owner: {
    marginTop: 4,
    color: '#64748b',
    fontSize: 13,
  },
  badge: {
    borderRadius: 999,
    padding: '5px 10px',
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: 0.4,
  },
  fieldList: {
    display: 'grid',
    gap: 8,
  },
  fieldRow: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: 12,
    borderTop: '1px solid #f1f5f9',
    paddingTop: 8,
  },
  fieldLabel: {
    color: '#64748b',
    fontSize: 13,
  },
  fieldValue: {
    color: '#0f172a',
    fontSize: 13,
    fontWeight: 600,
    textAlign: 'right',
  },
  cardActions: {
    marginTop: 10,
    display: 'flex',
    gap: 8,
  },
  secondaryActionButton: {
    border: '1px solid #cbd5e1',
    background: 'white',
    color: '#334155',
    borderRadius: 8,
    padding: '7px 11px',
    cursor: 'pointer',
    fontWeight: 600,
  },
  dangerActionButton: {
    border: '1px solid #dc2626',
    background: '#dc2626',
    color: 'white',
    borderRadius: 8,
    padding: '7px 11px',
    cursor: 'pointer',
    fontWeight: 600,
  },
  updatedAt: {
    marginTop: 2,
    color: '#94a3b8',
    fontSize: 12,
  },
  modalBackdrop: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(15, 23, 42, 0.55)',
    display: 'grid',
    placeItems: 'center',
    zIndex: 9999,
    padding: 16,
  },
  modalCard: {
    width: '100%',
    maxWidth: 640,
    background: 'white',
    borderRadius: 12,
    border: '1px solid #e2e8f0',
    padding: 16,
  },
  modalTitle: {
    margin: '0 0 14px 0',
    color: '#0f172a',
  },
  modalFields: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: 10,
  },
  fieldBlock: {
    display: 'grid',
    gap: 6,
  },
  fieldCaption: {
    fontSize: 13,
    color: '#475569',
    fontWeight: 600,
  },
  input: {
    border: '1px solid #cbd5e1',
    borderRadius: 8,
    padding: '8px 10px',
    fontSize: 14,
  },
  modalActions: {
    marginTop: 14,
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 8,
  },
};

export default DeviceTypePage;
