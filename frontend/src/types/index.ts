export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  device_count: number;
}

export interface Device {
  id: number;
  user: number;
  user_username: string;
  name: string;
  status: 'online' | 'offline' | 'error';
  device_type: string;
  created_at: string;
  updated_at: string;
}

export interface Battery extends Device {
  capacity_kwh: number;
  current_charge_kwh: number;
  charge_percentage: number;
  max_charge_rate_kw: number;
  max_discharge_rate_kw: number;
}

export interface ElectricVehicle extends Device {
  capacity_kwh: number;
  current_charge_kwh: number;
  charge_percentage: number;
  max_charge_rate_kw: number;
  max_discharge_rate_kw: number;
  mode: 'charging' | 'discharging' | 'offline';
  last_seen_at: string | null;
  driving_efficiency_kwh_per_hour: number;
}

export interface SolarPanel extends Device {
  panel_area_m2: number;
  efficiency: number;
  max_capacity_w: number;
  latitude: number;
  longitude: number;
}

export interface Generator extends Device {
  rated_output_w: number;
}

export interface AirConditioner extends Device {
  rated_power_w: number;
  min_power_w: number;
  max_power_w: number;
}

export interface Heater extends Device {
  rated_power_w: number;
  min_power_w: number;
  max_power_w: number;
}

export interface DeviceStats {
  total: number;
  online: number;
  offline: number;
  error: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}
