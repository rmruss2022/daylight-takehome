import React from 'react';
import DeviceTypePage from '../components/DeviceTypePage';
import { electricVehiclesAPI } from '../api/services';

const ElectricVehicles: React.FC = () => (
  <DeviceTypePage
    title="🚗 Electric Vehicles"
    subtitle="Track EV mode, charge levels, and charging/discharging limits."
    emptyMessage="No electric vehicles found."
    fetchItems={electricVehiclesAPI.getAll}
    createItem={electricVehiclesAPI.create}
    updateItem={electricVehiclesAPI.update}
    deleteItem={electricVehiclesAPI.delete}
    fields={[
      { key: 'mode', label: 'Mode', formatter: (v) => String(v || 'offline').toUpperCase() },
      { key: 'capacity_kwh', label: 'Capacity', formatter: (v) => `${Number(v || 0).toFixed(1)} kWh` },
      { key: 'current_charge_kwh', label: 'Current Charge', formatter: (v) => `${Number(v || 0).toFixed(1)} kWh` },
      { key: 'charge_percentage', label: 'Charge Level', formatter: (v) => `${Number(v || 0).toFixed(1)}%` },
      { key: 'max_charge_rate_kw', label: 'Max Charge Rate', formatter: (v) => `${Number(v || 0).toFixed(1)} kW` },
      { key: 'max_discharge_rate_kw', label: 'Max Discharge Rate', formatter: (v) => `${Number(v || 0).toFixed(1)} kW` },
      {
        key: 'last_seen_at',
        label: 'Last Seen',
        formatter: (v) => (v ? new Date(v).toLocaleString() : '-'),
      },
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
      {
        key: 'mode',
        label: 'Mode',
        type: 'select',
        required: true,
        defaultValue: 'offline',
        options: [
          { label: 'Charging', value: 'charging' },
          { label: 'Discharging', value: 'discharging' },
          { label: 'Offline', value: 'offline' },
        ],
      },
      { key: 'capacity_kwh', label: 'Capacity (kWh)', type: 'number', required: true, step: '0.1', min: 0 },
      { key: 'current_charge_kwh', label: 'Current Charge (kWh)', type: 'number', required: true, step: '0.1', min: 0 },
      { key: 'max_charge_rate_kw', label: 'Max Charge Rate (kW)', type: 'number', required: true, step: '0.1', min: 0 },
      { key: 'max_discharge_rate_kw', label: 'Max Discharge Rate (kW)', type: 'number', required: true, step: '0.1', min: 0 },
      {
        key: 'driving_efficiency_kwh_per_hour',
        label: 'Driving Efficiency (kWh/h)',
        type: 'number',
        required: true,
        step: '0.1',
        min: 0,
      },
    ]}
  />
);

export default ElectricVehicles;
