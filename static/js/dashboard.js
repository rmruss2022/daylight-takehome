/**
 * DASHBOARD MAIN SCRIPT
 * Handles data fetching, updates, and UI interactions
 */

// Configuration
const CONFIG = {
  graphqlEndpoint: '/graphql/',
  refreshInterval: 5000, // 5 seconds
  maxRetries: 3,
  animationDuration: 500
};

// State management
const state = {
  energyStats: null,
  devices: [],
  isLoading: false,
  retryCount: 0,
  lastUpdate: null
};

/**
 * GraphQL Queries
 */
const QUERIES = {
  energyStats: `
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
    }
  `,

  devices: `
    query {
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
          capacityKwh
          currentChargeKwh
          maxChargeRateKw
          maxDischargeRateKw
          mode
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
  `
};

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Fetch data from GraphQL endpoint
 */
async function fetchGraphQL(query) {
  try {
    const csrftoken = getCookie('csrftoken');

    const response = await fetch(CONFIG.graphqlEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      credentials: 'same-origin',
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.errors) {
      console.error('GraphQL errors:', result.errors);
      throw new Error(result.errors[0].message);
    }

    return result.data;
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

/**
 * Update energy statistics display
 */
function updateEnergyStats(stats) {
  if (!stats) return;

  // Update production
  animateValue('production-value', stats.currentProduction || 0, 'W');
  updateProgressBar('production-bar', Math.min((stats.currentProduction || 0) / 10000 * 100, 100));

  // Update consumption
  animateValue('consumption-value', stats.currentConsumption || 0, 'W');
  updateProgressBar('consumption-bar', Math.min((stats.currentConsumption || 0) / 10000 * 100, 100));

  // Update storage
  const storage = stats.currentStorage || { percentage: 0, currentLevelWh: 0, totalCapacityWh: 0 };
  animateValue('storage-percentage', storage.percentage || 0, '%', 1);
  updateProgressBar('storage-bar', storage.percentage || 0);

  const currentKwh = ((storage.currentLevelWh || 0) / 1000).toFixed(1);
  const totalKwh = ((storage.totalCapacityWh || 0) / 1000).toFixed(1);
  document.getElementById('storage-current').textContent = currentKwh;
  document.getElementById('storage-total').textContent = totalKwh;

  // Update net grid flow
  const netFlow = stats.netGridFlow || 0;
  animateValue('grid-flow-value', Math.abs(netFlow), 'W');

  const flowTrend = document.getElementById('grid-flow-trend');
  const flowIcon = document.getElementById('grid-flow-icon');
  const flowStatus = document.getElementById('grid-flow-status');

  if (netFlow > 100) {
    flowTrend.className = 'stat-trend negative';
    flowIcon.textContent = '⬆️';
    flowStatus.textContent = 'Drawing from Grid';
  } else if (netFlow < -100) {
    flowTrend.className = 'stat-trend positive';
    flowIcon.textContent = '⬇️';
    flowStatus.textContent = 'Sending to Grid';
  } else {
    flowTrend.className = 'stat-trend';
    flowIcon.textContent = '⚖️';
    flowStatus.textContent = 'Balanced';
  }

  // Update flow visualization
  updateFlowVisualization(stats);

  // Update net flow center value
  const netFlowCenter = document.getElementById('net-flow-center');
  netFlowCenter.textContent = `${netFlow >= 0 ? '+' : ''}${Math.round(netFlow)} W`;
  netFlowCenter.className = `net-flow-value ${netFlow > 0 ? 'negative' : netFlow < 0 ? 'positive' : ''}`;
}

/**
 * Update flow visualization with breakdown
 */
function updateFlowVisualization(stats) {
  // These would come from detailed device data
  // For now, using placeholder logic
  document.getElementById('solar-production').textContent = Math.round((stats.currentProduction || 0) * 0.7);
  document.getElementById('generator-production').textContent = Math.round((stats.currentProduction || 0) * 0.3);

  document.getElementById('hvac-consumption').textContent = Math.round((stats.currentConsumption || 0) * 0.6);

  const storageFlow = stats.currentStorageFlow || 0;
  document.getElementById('battery-flow').textContent = Math.round(storageFlow * 0.6);
  document.getElementById('ev-flow').textContent = Math.round(storageFlow * 0.4);
}

/**
 * Animate numeric value changes
 */
function animateValue(elementId, endValue, suffix = '', decimals = 0) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const startValue = parseFloat(element.textContent) || 0;
  const duration = CONFIG.animationDuration;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing function (ease-out)
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = startValue + (endValue - startValue) * eased;

    element.textContent = current.toFixed(decimals);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

/**
 * Update progress bar width
 */
function updateProgressBar(elementId, percentage) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.style.width = `${Math.min(Math.max(percentage, 0), 100)}%`;
}

/**
 * Render devices grid
 */
function renderDevices(devices) {
  const grid = document.getElementById('device-grid');
  if (!grid) return;

  if (!devices || devices.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚡</div>
        <h3 class="empty-state-title">No Devices Connected</h3>
        <p class="empty-state-text">Add devices to start monitoring your energy usage</p>
        <a href="/admin/devices/" class="btn btn-primary">Manage Devices</a>
      </div>
    `;
    return;
  }

  grid.innerHTML = devices.map(device => {
    const typename = device.__typename || '';
    const deviceType = getDeviceCategoryFromTypename(typename);
    const icon = getDeviceIconFromTypename(typename);
    const specs = getDeviceSpecs(device);

    return `
      <div class="device-card ${deviceType}" data-device-id="${device.id}">
        <div class="device-card-header">
          <div class="device-info">
            <h3 class="device-name">${device.name}</h3>
            <div class="device-type">${formatTypename(typename)}</div>
          </div>
          <div class="device-icon ${deviceType.toLowerCase()}">${icon}</div>
        </div>

        <div class="device-stats">
          ${specs.map(spec => `
            <div class="device-stat">
              <span class="device-stat-label">${spec.label}</span>
              <span class="device-stat-value">${spec.value}</span>
            </div>
          `).join('')}
        </div>

        <div style="margin-top: var(--space-4);">
          ${device.mode 
            ? (device.mode === 'CHARGING' 
                ? '<span class="badge badge-online"><span class="badge-dot"></span> Charging</span>'
                : device.mode === 'DRIVING'
                  ? '<span class="badge badge-offline"><span class="badge-dot"></span> Driving</span>'
                  : '<span class="badge badge-offline"><span class="badge-dot"></span> Disconnected</span>')
            : (device.status === 'ONLINE'
                ? '<span class="badge badge-online"><span class="badge-dot"></span> Online</span>'
                : '<span class="badge badge-offline"><span class="badge-dot"></span> Offline</span>')
          }
        </div>

        ${deviceType === 'storage' && device.capacityKwh ? renderStorageViz(device) : ''}
      </div>
    `;
  }).join('');
}

/**
 * Render storage visualization for batteries and EVs
 */
function renderStorageViz(device) {
  const percentage = (device.currentChargeKwh / device.capacityKwh * 100).toFixed(1);
  return `
    <div class="storage-viz">
      <div class="storage-level">
        <span class="storage-percentage">${percentage}%</span>
        <span class="storage-capacity">${device.currentChargeKwh.toFixed(1)} / ${device.capacityKwh.toFixed(1)} kWh</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill storage" style="width: ${percentage}%"></div>
      </div>
    </div>
  `;
}

/**
 * Get device category from GraphQL typename
 */
function getDeviceCategoryFromTypename(typename) {
  const categories = {
    'SolarPanelType': 'production',
    'GeneratorType': 'production',
    'BatteryType': 'storage',
    'ElectricVehicleType': 'storage',
    'AirConditionerType': 'consumption',
    'HeaterType': 'consumption'
  };
  return categories[typename] || 'device';
}

/**
 * Get device icon from GraphQL typename
 */
function getDeviceIconFromTypename(typename) {
  const icons = {
    'SolarPanelType': '☀️',
    'GeneratorType': '⚙️',
    'BatteryType': '🔋',
    'ElectricVehicleType': '🚗',
    'AirConditionerType': '❄️',
    'HeaterType': '🔥'
  };
  return icons[typename] || '⚡';
}

/**
 * Format typename for display
 */
function formatTypename(typename) {
  // Remove 'Type' suffix and split by capital letters
  const name = typename.replace('Type', '');
  return name.replace(/([A-Z])/g, ' $1').trim();
}

/**
 * Get device category (production, consumption, storage) - legacy support
 */
function getDeviceCategory(deviceType) {
  const categories = {
    'solar_panel': 'production',
    'generator': 'production',
    'battery': 'storage',
    'electric_vehicle': 'storage',
    'air_conditioner': 'consumption',
    'heater': 'consumption'
  };
  return categories[deviceType] || 'device';
}

/**
 * Get device icon emoji - legacy support
 */
function getDeviceIcon(deviceType) {
  const icons = {
    'solar_panel': '☀️',
    'generator': '⚙️',
    'battery': '🔋',
    'electric_vehicle': '🚗',
    'air_conditioner': '❄️',
    'heater': '🔥'
  };
  return icons[deviceType] || '⚡';
}

/**
 * Format device type for display - legacy support
 */
function formatDeviceType(deviceType) {
  return deviceType.split('_').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}

/**
 * Get device specifications for display
 */
function getDeviceSpecs(device) {
  const specs = [];

  // Solar Panel fields
  if (device.maxCapacityW !== undefined) {
    specs.push({ label: 'Max Output', value: `${Math.round(device.maxCapacityW)} W` });
  }
  if (device.panelAreaM2 !== undefined) {
    specs.push({ label: 'Panel Area', value: `${device.panelAreaM2} m²` });
  }
  if (device.efficiency !== undefined) {
    specs.push({ label: 'Efficiency', value: `${(device.efficiency * 100).toFixed(1)}%` });
  }

  // Generator fields
  if (device.ratedOutputW !== undefined) {
    specs.push({ label: 'Rated Output', value: `${Math.round(device.ratedOutputW)} W` });
  }

  // Consumption device fields
  if (device.ratedPowerW !== undefined) {
    specs.push({ label: 'Rated Power', value: `${Math.round(device.ratedPowerW)} W` });
  }
  if (device.minPowerW !== undefined) {
    specs.push({ label: 'Min Power', value: `${Math.round(device.minPowerW)} W` });
  }
  if (device.maxPowerW !== undefined) {
    specs.push({ label: 'Max Power', value: `${Math.round(device.maxPowerW)} W` });
  }

  // Storage device fields (Battery, EV)
  if (device.capacityKwh !== undefined) {
    specs.push({ label: 'Capacity', value: `${device.capacityKwh.toFixed(1)} kWh` });
  }
  if (device.maxChargeRateKw !== undefined) {
    specs.push({ label: 'Max Charge', value: `${device.maxChargeRateKw.toFixed(1)} kW` });
  }

  return specs;
}

/**
 * Update last update timestamp
 */
function updateTimestamp() {
  const now = new Date();
  const timestamp = now.toLocaleTimeString();
  const element = document.getElementById('last-update');
  if (element) {
    element.textContent = `Last updated: ${timestamp}`;
  }
  state.lastUpdate = now;
}

/**
 * Fetch and update all data
 */
async function refreshData() {
  if (state.isLoading) return;

  state.isLoading = true;

  try {
    console.log('Fetching energy stats...');
    // Fetch energy stats
    const energyData = await fetchGraphQL(QUERIES.energyStats);
    console.log('Energy data received:', energyData);
    state.energyStats = energyData.energyStats;
    updateEnergyStats(state.energyStats);

    // Fetch devices (less frequently)
    if (!state.devices.length || Math.random() < 0.2) {
      console.log('Fetching devices...');
      const devicesData = await fetchGraphQL(QUERIES.devices);
      console.log('Devices data received:', devicesData);
      state.devices = devicesData.allDevices || [];
      renderDevices(state.devices);
    }

    updateTimestamp();
    state.retryCount = 0;

  } catch (error) {
    console.error('Error refreshing data:', error);
    state.retryCount++;

    // Show error message to user
    showError(`Failed to load data: ${error.message}`);

    if (state.retryCount >= CONFIG.maxRetries) {
      console.error('Max retries reached. Stopping auto-refresh.');
      showError('Unable to connect to server. Please refresh the page.');
    }
  } finally {
    state.isLoading = false;
  }
}

/**
 * Show error message to user
 */
function showError(message) {
  // Create error notification if it doesn't exist
  let errorDiv = document.getElementById('error-notification');
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.id = 'error-notification';
    errorDiv.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: rgba(255, 71, 87, 0.95);
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
      z-index: 1000;
      max-width: 400px;
      font-family: var(--font-body);
      animation: slide-up 0.3s;
    `;
    document.body.appendChild(errorDiv);
  }
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';

  // Auto-hide after 5 seconds
  setTimeout(() => {
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
  }, 5000);
}

/**
 * Initialize dashboard
 */
async function initDashboard() {
  console.log('Initializing energy dashboard...');

  // Initial data fetch
  await refreshData();

  // Set up auto-refresh
  setInterval(refreshData, CONFIG.refreshInterval);

  // Add event listeners
  setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // User menu (placeholder)
  const userMenu = document.getElementById('user-menu');
  if (userMenu) {
    userMenu.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('User menu clicked');
      // Could open a dropdown menu here
    });
  }

  // Add other event listeners as needed
}

/**
 * Start the application when DOM is ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}

// Export for use in other modules
window.DaylightDashboard = {
  state,
  refreshData,
  updateEnergyStats,
  renderDevices
};
