import React from 'react';
import DeviceTypePage from '../components/DeviceTypePage';
import { generatorsAPI } from '../api/services';

const Generators: React.FC = () => (
  <DeviceTypePage
    title="⚡ Generators"
    subtitle="Inspect generator output ratings and operational status."
    emptyMessage="No generators found."
    fetchItems={generatorsAPI.getAll}
    createItem={generatorsAPI.create}
    updateItem={generatorsAPI.update}
    deleteItem={generatorsAPI.delete}
    fields={[{ key: 'rated_output_w', label: 'Rated Output', formatter: (v) => `${Math.round(Number(v || 0))} W` }]}
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
      { key: 'rated_output_w', label: 'Rated Output (W)', type: 'number', required: true, step: '1', min: 0 },
    ]}
  />
);

export default Generators;
