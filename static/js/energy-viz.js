/**
 * ENERGY VISUALIZATION
 * Advanced canvas-based energy flow particle effects
 */

class EnergyParticle {
  constructor(x, y, targetX, targetY, color) {
    this.x = x;
    this.y = y;
    this.targetX = targetX;
    this.targetY = targetY;
    this.color = color;
    this.size = Math.random() * 3 + 1;
    this.speed = Math.random() * 0.02 + 0.01;
    this.progress = 0;
    this.opacity = 1;
    this.life = 1;
  }

  update() {
    this.progress += this.speed;

    // Bezier curve for smooth flow
    const cp1x = this.x + (this.targetX - this.x) * 0.3;
    const cp1y = this.y - 50;
    const cp2x = this.x + (this.targetX - this.x) * 0.7;
    const cp2y = this.targetY - 50;

    const t = this.progress;
    const invT = 1 - t;

    this.x = invT * invT * invT * this.x +
             3 * invT * invT * t * cp1x +
             3 * invT * t * t * cp2x +
             t * t * t * this.targetX;

    this.y = invT * invT * invT * this.y +
             3 * invT * invT * t * cp1y +
             3 * invT * t * t * cp2y +
             t * t * t * this.targetY;

    // Fade out near the end
    if (this.progress > 0.8) {
      this.opacity = (1 - this.progress) * 5;
    }

    this.life = 1 - this.progress;
  }

  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.opacity;
    ctx.fillStyle = this.color;
    ctx.shadowBlur = 15;
    ctx.shadowColor = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  isDead() {
    return this.progress >= 1;
  }
}

class EnergyFlowVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      console.warn(`Canvas ${canvasId} not found`);
      return;
    }

    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.isRunning = false;

    this.colors = {
      production: '#00ff88',
      consumption: '#ff8c42',
      storage: '#00d4ff'
    };

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;

    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  addParticle(type, count = 1) {
    if (!this.canvas) return;

    const width = this.canvas.width;
    const height = this.canvas.height;

    for (let i = 0; i < count; i++) {
      let startX, startY, endX, endY;

      switch (type) {
        case 'production':
          startX = Math.random() * width * 0.2;
          startY = Math.random() * height;
          endX = width * 0.5 + Math.random() * 100 - 50;
          endY = height * 0.5 + Math.random() * 100 - 50;
          break;

        case 'consumption':
          startX = width * 0.5 + Math.random() * 100 - 50;
          startY = height * 0.5 + Math.random() * 100 - 50;
          endX = width * 0.8 + Math.random() * width * 0.2;
          endY = Math.random() * height;
          break;

        case 'storage':
          startX = width * 0.5 + Math.random() * 100 - 50;
          startY = height * 0.5 + Math.random() * 100 - 50;
          endX = width * 0.8 + Math.random() * width * 0.2;
          endY = height * 0.7 + Math.random() * height * 0.3;
          break;

        default:
          return;
      }

      this.particles.push(
        new EnergyParticle(startX, startY, endX, endY, this.colors[type])
      );
    }
  }

  update() {
    if (!this.canvas || !this.ctx) return;

    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Update and draw particles
    this.particles = this.particles.filter(particle => {
      particle.update();
      particle.draw(this.ctx);
      return !particle.isDead();
    });
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.animate();
  }

  stop() {
    this.isRunning = false;
  }

  animate() {
    if (!this.isRunning) return;

    this.update();
    requestAnimationFrame(() => this.animate());
  }

  setFlowRate(type, rate) {
    // Rate is in watts, adjust particle spawn rate accordingly
    const particlesPerFrame = Math.min(Math.max(rate / 1000, 0), 5);

    if (Math.random() < particlesPerFrame) {
      const count = Math.ceil(particlesPerFrame);
      this.addParticle(type, count);
    }
  }
}

/**
 * Energy Meter Circle Visualization
 */
class EnergyMeter {
  constructor(containerId, type, maxValue = 10000) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.type = type;
    this.maxValue = maxValue;
    this.currentValue = 0;
    this.targetValue = 0;

    this.colors = {
      production: '#00ff88',
      consumption: '#ff8c42',
      storage: '#00d4ff'
    };

    this.create();
  }

  create() {
    const html = `
      <svg class="meter-circle" viewBox="0 0 200 200">
        <circle class="meter-bg" cx="100" cy="100" r="90"></circle>
        <circle class="meter-progress ${this.type}"
                cx="100" cy="100" r="90"
                stroke-dasharray="565.48"
                stroke-dashoffset="565.48"
                id="${this.type}-progress"></circle>
      </svg>
      <div class="meter-value">
        <div class="meter-number" id="${this.type}-number">0</div>
        <div class="meter-label">${this.type}</div>
      </div>
    `;

    this.container.innerHTML = html;
    this.progressCircle = document.getElementById(`${this.type}-progress`);
    this.numberElement = document.getElementById(`${this.type}-number`);
  }

  setValue(value) {
    this.targetValue = Math.min(value, this.maxValue);
    this.animate();
  }

  animate() {
    const diff = this.targetValue - this.currentValue;
    this.currentValue += diff * 0.1;

    if (Math.abs(diff) < 0.5) {
      this.currentValue = this.targetValue;
    }

    // Update circle
    const percentage = (this.currentValue / this.maxValue) * 100;
    const circumference = 565.48;
    const offset = circumference - (percentage / 100) * circumference;

    if (this.progressCircle) {
      this.progressCircle.style.strokeDashoffset = offset;
    }

    // Update number
    if (this.numberElement) {
      this.numberElement.textContent = Math.round(this.currentValue);
    }

    if (Math.abs(diff) >= 0.5) {
      requestAnimationFrame(() => this.animate());
    }
  }
}

/**
 * Aurora Background Effect
 */
class AuroraBackground {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      console.warn(`Canvas ${canvasId} not found, using CSS aurora`);
      return;
    }

    this.ctx = this.canvas.getContext('2d');
    this.time = 0;
    this.resize();

    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;

    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  draw() {
    if (!this.canvas || !this.ctx) return;

    const { width, height } = this.canvas;
    this.ctx.clearRect(0, 0, width, height);

    // Create aurora gradient layers
    const gradients = [
      {
        x: width * 0.5 + Math.sin(this.time * 0.001) * width * 0.3,
        y: height * 0.2,
        radius: width * 0.4,
        color: 'rgba(180, 75, 243, 0.15)'
      },
      {
        x: width * 0.8 + Math.cos(this.time * 0.0015) * width * 0.2,
        y: height * 0.5,
        radius: width * 0.35,
        color: 'rgba(0, 212, 255, 0.12)'
      },
      {
        x: width * 0.2 + Math.sin(this.time * 0.0012) * width * 0.2,
        y: height * 0.8,
        radius: width * 0.45,
        color: 'rgba(0, 255, 136, 0.1)'
      }
    ];

    gradients.forEach(g => {
      const gradient = this.ctx.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.radius);
      gradient.addColorStop(0, g.color);
      gradient.addColorStop(1, 'transparent');

      this.ctx.fillStyle = gradient;
      this.ctx.fillRect(0, 0, width, height);
    });

    this.time += 16;
  }

  start() {
    this.animate();
  }

  animate() {
    this.draw();
    requestAnimationFrame(() => this.animate());
  }
}

/**
 * Initialize visualizations
 */
function initVisualizations() {
  // Note: These would require canvas elements in the HTML
  // For now, we're using CSS-based animations

  // Example usage if canvas elements exist:
  // const flowViz = new EnergyFlowVisualizer('energy-flow-canvas');
  // flowViz.start();

  // Update flow visualization based on energy stats
  if (window.DaylightDashboard) {
    const originalUpdate = window.DaylightDashboard.updateEnergyStats;

    window.DaylightDashboard.updateEnergyStats = function(stats) {
      originalUpdate(stats);

      // Additional visual effects can be triggered here
      // Example: flowViz.setFlowRate('production', stats.currentProduction);
    };
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initVisualizations);
} else {
  initVisualizations();
}

// Export for external use
window.EnergyViz = {
  EnergyFlowVisualizer,
  EnergyMeter,
  AuroraBackground,
  EnergyParticle
};
