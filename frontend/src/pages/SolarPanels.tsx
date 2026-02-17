import React from 'react';
import DeviceTypePage from '../components/DeviceTypePage';
import { solarPanelsAPI } from '../api/services';

const SolarPanels: React.FC = () => (
  <DeviceTypePage
    title="☀️ Solar Panels"
    subtitle="View panel efficiency, output limits, and configured location."
    emptyMessage="No solar panels found."
    fetchItems={solarPanelsAPI.getAll}
    createItem={solarPanelsAPI.create}
    updateItem={solarPanelsAPI.update}
    deleteItem={solarPanelsAPI.delete}
    fields={[
      { key: 'panel_area_m2', label: 'Panel Area', formatter: (v) => `${Number(v || 0).toFixed(2)} m²` },
      { key: 'efficiency', label: 'Efficiency', formatter: (v) => `${(Number(v || 0) * 100).toFixed(1)}%` },
      { key: 'max_capacity_w', label: 'Max Capacity', formatter: (v) => `${Math.round(Number(v || 0))} W` },
      { key: 'latitude', label: 'Latitude', formatter: (v) => Number(v || 0).toFixed(4) },
      { key: 'longitude', label: 'Longitude', formatter: (v) => Number(v || 0).toFixed(4) },
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
      { key: 'panel_area_m2', label: 'Panel Area (m²)', type: 'number', required: true, step: '0.01', min: 0 },
      { key: 'efficiency', label: 'Efficiency (0-1)', type: 'number', required: true, step: '0.01', min: 0 },
      { key: 'max_capacity_w', label: 'Max Capacity (W)', type: 'number', required: true, step: '1', min: 0 },
      { key: 'latitude', label: 'Latitude', type: 'number', required: true, step: '0.0001' },
      { key: 'longitude', label: 'Longitude', type: 'number', required: true, step: '0.0001' },
    ]}
  />
);

export default SolarPanels;
