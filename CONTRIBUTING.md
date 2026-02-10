# Contributing to Daylight Energy Management System

Thank you for your interest in contributing! This guide will help you get started with development and understand our workflow.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Git** installed and configured
- **Docker Desktop** installed and running
- **Python 3.11+** (for local development without Docker)
- **Node.js 18+** (for frontend development)
- Basic knowledge of Django, React, and GraphQL

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Daylight.git
   cd Daylight
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/Daylight.git
   ```

## Development Setup

### Using Docker (Recommended)

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start services:**
   ```bash
   docker compose up --build
   ```

3. **Run migrations:**
   ```bash
   docker compose exec web python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. **Load sample data:**
   ```bash
   docker compose exec web python manage.py seed_devices
   ```

### Local Development (Without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL and Redis:**
   - Install PostgreSQL and Redis locally
   - Update `.env` with local connection strings

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Celery worker (separate terminal):**
   ```bash
   celery -A config worker -l info
   ```

6. **Start Celery beat (separate terminal):**
   ```bash
   celery -A config beat -l info
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Development

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

Frontend will be available at http://localhost:3000

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/refactor-description` - Code refactoring
- `test/test-description` - Test additions/updates

### 2. Make Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and focused

### 3. Test Your Changes

```bash
# Run all tests
docker compose exec web pytest

# Run with coverage
docker compose exec web pytest --cov=apps --cov-report=html

# Run specific tests
docker compose exec web pytest tests/test_devices/test_models.py

# Frontend tests
cd frontend && npm test
```

### 4. Commit Changes

Follow our [commit message guidelines](#commit-message-guidelines):

```bash
git add .
git commit -m "feat: Add solar panel efficiency calculator"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template
5. Submit for review

## Coding Standards

### Python (Backend)

#### Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Prefer double quotes for strings
- **Imports**: Organized in three groups (standard library, third-party, local)

#### Example

```python
"""Module docstring."""

# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from django.db import models
from strawberry import type

# Local imports
from apps.devices.models.base import Device


class SolarPanel(Device):
    """Solar panel device model.
    
    Attributes:
        panel_area_m2: Panel area in square meters
        efficiency: Conversion efficiency (0-1)
        max_capacity_w: Maximum power output in watts
    """
    
    panel_area_m2 = models.FloatField(
        help_text="Panel area in square meters"
    )
    efficiency = models.FloatField(
        help_text="Conversion efficiency (0-1)"
    )
    max_capacity_w = models.FloatField(
        help_text="Maximum power output in watts"
    )
    
    def calculate_output(self, irradiance: float) -> float:
        """Calculate power output based on irradiance.
        
        Args:
            irradiance: Solar irradiance in W/m²
            
        Returns:
            Power output in watts
        """
        return self.panel_area_m2 * self.efficiency * irradiance
```

#### Code Quality Tools

- **Linting**: Use `flake8` or `pylint`
- **Formatting**: Use `black` for auto-formatting
- **Type hints**: Use type annotations where applicable
- **Docstrings**: Required for all public functions/classes

### TypeScript/React (Frontend)

#### Style Guide

- **Line length**: 100 characters maximum
- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings, double for JSX props
- **Semicolons**: Required
- **Components**: Use functional components with hooks

#### Example

```typescript
import React, { useState, useEffect } from 'react';
import { DeviceService } from '../api/devices';
import { Device } from '../types';

interface DeviceListProps {
  userId: number;
}

export const DeviceList: React.FC<DeviceListProps> = ({ userId }) => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const data = await DeviceService.getAll();
        setDevices(data);
      } catch (error) {
        console.error('Failed to fetch devices:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDevices();
  }, [userId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="device-list">
      {devices.map((device) => (
        <div key={device.id} className="device-item">
          {device.name}
        </div>
      ))}
    </div>
  );
};
```

#### Code Quality Tools

- **Linting**: ESLint with TypeScript plugin
- **Formatting**: Prettier
- **Type checking**: TypeScript compiler

### Django-Specific Guidelines

#### Models

- Always include `help_text` for fields
- Use `related_name` for reverse relationships
- Add `__str__()` method for admin display
- Use model methods for business logic

#### Views

- Use Django REST Framework ViewSets
- Implement proper permission classes
- Add docstrings explaining endpoint behavior
- Handle errors gracefully

#### GraphQL

- Use Strawberry types and fields
- Add docstrings for schema documentation
- Implement proper permission classes
- Use unions for polymorphic types

### Database

- Always create migrations for model changes
- Test migrations in both directions (up and down)
- Use descriptive migration names
- Don't edit existing migrations (create new ones)

## Testing

### Writing Tests

#### Backend Tests (Pytest)

```python
"""Tests for solar panel simulator."""

import pytest
from datetime import datetime
from apps.simulation.simulators.solar import SolarSimulator
from apps.devices.models import SolarPanel


@pytest.fixture
def solar_panel(user):
    """Create a test solar panel."""
    return SolarPanel.objects.create(
        user=user,
        name="Test Solar",
        panel_area_m2=20.0,
        efficiency=0.20,
        max_capacity_w=4000.0,
        latitude=37.77,
        longitude=-122.42,
    )


def test_solar_output_at_noon(solar_panel):
    """Test solar panel output at solar noon."""
    simulator = SolarSimulator(solar_panel)
    noon = datetime(2024, 6, 21, 12, 0)  # Summer solstice noon
    
    result = simulator.simulate(current_time=noon)
    
    assert result['current'] > 0
    assert result['current'] <= solar_panel.max_capacity_w


def test_solar_output_at_night(solar_panel):
    """Test solar panel output at night."""
    simulator = SolarSimulator(solar_panel)
    midnight = datetime(2024, 6, 21, 0, 0)
    
    result = simulator.simulate(current_time=midnight)
    
    assert result['current'] == 0
```

#### Frontend Tests (Jest/React Testing Library)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DeviceList } from './DeviceList';
import { DeviceService } from '../api/devices';

jest.mock('../api/devices');

describe('DeviceList', () => {
  it('renders device list', async () => {
    const mockDevices = [
      { id: 1, name: 'Solar Panel', status: 'online' },
      { id: 2, name: 'Battery', status: 'online' },
    ];
    
    (DeviceService.getAll as jest.Mock).mockResolvedValue(mockDevices);
    
    render(<DeviceList userId={1} />);
    
    await waitFor(() => {
      expect(screen.getByText('Solar Panel')).toBeInTheDocument();
      expect(screen.getByText('Battery')).toBeInTheDocument();
    });
  });
});
```

### Test Coverage

- Aim for **80%+ coverage** on backend code
- Test all business logic and edge cases
- Include integration tests for API endpoints
- Test error handling and validation

### Running Tests

```bash
# Backend tests
docker compose exec web pytest                    # Run all tests
docker compose exec web pytest -v                 # Verbose output
docker compose exec web pytest --cov=apps        # With coverage
docker compose exec web pytest tests/test_api/   # Specific directory

# Frontend tests
cd frontend
npm test                                          # Run all tests
npm test -- --coverage                           # With coverage
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code follows style guidelines
3. ✅ Documentation updated (if needed)
4. ✅ Commit messages follow guidelines
5. ✅ Branch is up to date with main

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Code review** by maintainers
3. **Requested changes** addressed
4. **Final approval** and merge

### Addressing Feedback

- Respond to all comments
- Make requested changes
- Push updates to same branch
- Request re-review when ready

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

### Examples

```bash
# Feature
feat(api): Add device statistics endpoint

# Bug fix
fix(simulation): Correct solar elevation calculation for southern hemisphere

# Documentation
docs(readme): Update installation instructions

# Refactor
refactor(models): Simplify device inheritance structure

# Test
test(devices): Add tests for battery charge logic

# Multiple changes
feat(dashboard): Add real-time energy monitoring

- Add WebSocket connection for live updates
- Implement auto-refresh every 60 seconds
- Add loading states and error handling

Closes #123
```

### Best Practices

- Use imperative mood ("Add feature" not "Added feature")
- Keep subject line under 50 characters
- Capitalize subject line
- Don't end subject with period
- Separate subject from body with blank line
- Wrap body at 72 characters
- Reference issues/PRs in footer

## Questions?

If you have questions or need help:

1. Check existing [documentation](README.md)
2. Search [existing issues](https://github.com/OWNER/Daylight/issues)
3. Ask in pull request comments
4. Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Daylight! 🌟
