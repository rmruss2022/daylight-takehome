import React from 'react';
import DeviceTypePage from '../components/DeviceTypePage';
import { airConditionersAPI } from '../api/services';

const AirConditioners: React.FC = () => (
  <DeviceTypePage
    title="❄️ Air Conditioners"
    subtitle="Review AC power bounds and real-time status."
    emptyMessage="No air conditioners found."
    fetchItems={airConditionersAPI.getAll}
    createItem={airConditionersAPI.create}
    updateItem={airConditionersAPI.update}
    deleteItem={airConditionersAPI.delete}
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

export default AirConditioners;
