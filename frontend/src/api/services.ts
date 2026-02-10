import axios from './axios';
import {
  User,
  Device,
  Battery,
  ElectricVehicle,
  SolarPanel,
  Generator,
  AirConditioner,
  Heater,
  DeviceStats,
  LoginCredentials,
  TokenResponse,
} from '../types/index';

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

  create: async (data: Partial<User>): Promise<User> => {
    const response = await axios.post('/users/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<User>): Promise<User> => {
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
