import React from 'react';
import DeviceTypePage from '../components/DeviceTypePage';
import { heatersAPI } from '../api/services';

const Heaters: React.FC = () => (
  <DeviceTypePage
    title="🔥 Heaters"
    subtitle="Review heater power limits and online/offline status."
    emptyMessage="No heaters found."
    fetchItems={heatersAPI.getAll}
    createItem={heatersAPI.create}
    updateItem={heatersAPI.update}
    deleteItem={heatersAPI.delete}
    fields={[
      { key: 'rated_power_w', label: 'Rated Power', formatter: (v) => `${Math.round(Number(v || 0))} W` },
      { key: 'min_power_w', label: 'Min Power', formatter: (v) => `${Math.round(Number(v || 0))} W` },
      { key: 'max_power_w', label: 'Max Power', formatter: (v) => `${Math.round(Number(v || 0))} W` },
    ]}
    formFields={[
      { key: 'name', label: 'Name', required: true, type: 'text' },
      {
        key: 'status',
        label: 'Status',
        type: 'select',
        required: true,
        defaultValue: 'online',
        options: [
          { label: 'Online', value: 'online' },
          { label: 'Offline', value: 'offline' },
          { label: 'Error', value: 'error' },
        ],
      },
      { key: 'rated_power_w', label: 'Rated Power (W)', type: 'number', required: true, step: '1', min: 0 },
      { key: 'min_power_w', label: 'Min Power (W)', type: 'number', required: true, step: '1', min: 0 },
      { key: 'max_power_w', label: 'Max Power (W)', type: 'number', required: true, step: '1', min: 0 },
    ]}
  />
);

export default Heaters;
