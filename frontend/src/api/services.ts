import axios from './axios';
import type {
  User,
  UserWritePayload,
  Device,
  Battery,
  ElectricVehicle,
  SolarPanel,
  Generator,
  AirConditioner,
  Heater,
  DeviceStats,
  EnergyStats,
  GraphQLDevice,
  LoginCredentials,
  TokenResponse,
} from '../types/index';

const GRAPHQL_URL = import.meta.env.VITE_GRAPHQL_URL || 'http://localhost:8000/graphql/';

async function graphqlRequest<T>(query: string): Promise<T> {
  const token = localStorage.getItem('access_token');
  const response = await fetch(GRAPHQL_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`GraphQL request failed (${response.status})`);
  }

  const payload = await response.json();
  if (payload.errors?.length) {
    throw new Error(payload.errors[0].message || 'GraphQL query error');
  }

  return payload.data as T;
}

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const response = await axios.post('/auth/token/', credentials);
    return response.data;
  },

  refreshToken: async (refresh: string): Promise<{ access: string }> => {
    const response = await axios.post('/auth/token/refresh/', { refresh });
    return response.data;
  },

  verifyToken: async (token: string): Promise<void> => {
    await axios.post('/auth/token/verify/', { token });
  },
};

// Users API
export const usersAPI = {
  getAll: async (): Promise<User[]> => {
    const response = await axios.get('/users/');
    return response.data.results || response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await axios.get('/users/me/');
    return response.data;
  },

  getById: async (id: number): Promise<User> => {
    const response = await axios.get(`/users/${id}/`);
    return response.data;
  },

  create: async (data: UserWritePayload): Promise<User> => {
    const response = await axios.post('/users/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<UserWritePayload>): Promise<User> => {
    const response = await axios.patch(`/users/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/users/${id}/`);
  },
};

// Devices API
export const devicesAPI = {
  getAll: async (): Promise<Device[]> => {
    const response = await axios.get('/devices/');
    return response.data.results || response.data;
  },

  getStats: async (): Promise<DeviceStats> => {
    const response = await axios.get('/devices/stats/');
    return response.data;
  },

  getById: async (id: number): Promise<Device> => {
    const response = await axios.get(`/devices/${id}/`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/devices/${id}/`);
  },
};

// Batteries API
export const batteriesAPI = {
  getAll: async (): Promise<Battery[]> => {
    const response = await axios.get('/batteries/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<Battery> => {
    const response = await axios.get(`/batteries/${id}/`);
    return response.data;
  },

  create: async (data: Partial<Battery>): Promise<Battery> => {
    const response = await axios.post('/batteries/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Battery>): Promise<Battery> => {
    const response = await axios.patch(`/batteries/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/batteries/${id}/`);
  },
};

// Electric Vehicles API
export const electricVehiclesAPI = {
  getAll: async (): Promise<ElectricVehicle[]> => {
    const response = await axios.get('/electric-vehicles/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<ElectricVehicle> => {
    const response = await axios.get(`/electric-vehicles/${id}/`);
    return response.data;
  },

  create: async (data: Partial<ElectricVehicle>): Promise<ElectricVehicle> => {
    const response = await axios.post('/electric-vehicles/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<ElectricVehicle>): Promise<ElectricVehicle> => {
    const response = await axios.patch(`/electric-vehicles/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/electric-vehicles/${id}/`);
  },
};

// Solar Panels API
export const solarPanelsAPI = {
  getAll: async (): Promise<SolarPanel[]> => {
    const response = await axios.get('/solar-panels/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<SolarPanel> => {
    const response = await axios.get(`/solar-panels/${id}/`);
    return response.data;
  },

  create: async (data: Partial<SolarPanel>): Promise<SolarPanel> => {
    const response = await axios.post('/solar-panels/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<SolarPanel>): Promise<SolarPanel> => {
    const response = await axios.patch(`/solar-panels/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/solar-panels/${id}/`);
  },
};

// Generators API
export const generatorsAPI = {
  getAll: async (): Promise<Generator[]> => {
    const response = await axios.get('/generators/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<Generator> => {
    const response = await axios.get(`/generators/${id}/`);
    return response.data;
  },

  create: async (data: Partial<Generator>): Promise<Generator> => {
    const response = await axios.post('/generators/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Generator>): Promise<Generator> => {
    const response = await axios.patch(`/generators/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/generators/${id}/`);
  },
};

// Air Conditioners API
export const airConditionersAPI = {
  getAll: async (): Promise<AirConditioner[]> => {
    const response = await axios.get('/air-conditioners/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<AirConditioner> => {
    const response = await axios.get(`/air-conditioners/${id}/`);
    return response.data;
  },

  create: async (data: Partial<AirConditioner>): Promise<AirConditioner> => {
    const response = await axios.post('/air-conditioners/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<AirConditioner>): Promise<AirConditioner> => {
    const response = await axios.patch(`/air-conditioners/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/air-conditioners/${id}/`);
  },
};

// Heaters API
export const heatersAPI = {
  getAll: async (): Promise<Heater[]> => {
    const response = await axios.get('/heaters/');
    return response.data.results || response.data;
  },

  getById: async (id: number): Promise<Heater> => {
    const response = await axios.get(`/heaters/${id}/`);
    return response.data;
  },

  create: async (data: Partial<Heater>): Promise<Heater> => {
    const response = await axios.post('/heaters/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Heater>): Promise<Heater> => {
    const response = await axios.patch(`/heaters/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/heaters/${id}/`);
  },
};

export const dashboardAPI = {
  getEnergyAndDevices: async (): Promise<{ energyStats: EnergyStats; allDevices: GraphQLDevice[] }> => {
    const query = `
      query {
        energyStats {
          currentProduction
          currentConsumption
          currentStorage {
            totalCapacityWh
            currentLevelWh
            percentage
          }
          currentStorageFlow
          netGridFlow
        }
        allDevices {
          __typename
          ... on SolarPanelType {
            id
            name
            status
            panelAreaM2
            efficiency
            maxCapacityW
          }
          ... on GeneratorType {
            id
            name
            status
            ratedOutputW
          }
          ... on BatteryType {
            id
            name
            status
            capacityKwh
            currentChargeKwh
            maxChargeRateKw
            maxDischargeRateKw
            chargePercentage
          }
          ... on ElectricVehicleType {
            id
            name
            status
            mode
            capacityKwh
            currentChargeKwh
            maxChargeRateKw
            maxDischargeRateKw
            chargePercentage
          }
          ... on AirConditionerType {
            id
            name
            status
            ratedPowerW
            minPowerW
            maxPowerW
          }
          ... on HeaterType {
            id
            name
            status
            ratedPowerW
            minPowerW
            maxPowerW
          }
        }
      }
    `;
    return graphqlRequest<{ energyStats: EnergyStats; allDevices: GraphQLDevice[] }>(query);
  },
};
