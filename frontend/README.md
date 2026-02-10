# Daylight React Frontend

A modern React frontend for the Daylight Django Energy Management System.

## Features

- ✅ **Modern React Stack**
  - React 18 + TypeScript
  - Vite for fast development
  - React Router for navigation
  
- ✅ **JWT Authentication**
  - Login/logout functionality
  - Token storage in localStorage
  - Automatic token refresh
  - Protected routes
  
- ✅ **REST API Integration**
  - Axios instance with interceptors
  - Automatic JWT token injection
  - Token refresh on 401 errors
  - Complete API service layer
  
- ✅ **Admin Features**
  - Dashboard with device statistics
  - User management (admin only)
  - Battery management
  - Electric Vehicle management
  - Solar Panel management
  - Generator management
  - Air Conditioner management
  - Heater management
  
- ✅ **Modern UI**
  - Responsive design
  - Clean, professional interface
  - Gradient backgrounds and cards
  - Status indicators
  - Loading states and error handling

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── axios.ts          # Axios instance with JWT interceptors
│   │   └── services.ts       # API service functions
│   ├── components/
│   │   ├── DeviceList.tsx    # Device listing component
│   │   └── Layout.tsx        # Main layout with sidebar navigation
│   ├── context/
│   │   └── AuthContext.tsx   # Authentication context provider
│   ├── pages/
│   │   ├── Login.tsx         # Login page
│   │   ├── Dashboard.tsx     # Main dashboard
│   │   ├── Batteries.tsx     # Battery management
│   │   └── Users.tsx         # User management (admin)
│   ├── types/
│   │   └── index.ts          # TypeScript type definitions
│   ├── App.tsx               # Main app component with routing
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles
├── .env                      # Environment configuration
├── Dockerfile                # Docker configuration
└── package.json              # Dependencies

```

## Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Django backend running on port 8000

### Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
# .env file (already configured)
VITE_API_BASE_URL=http://localhost:8000/api
```

3. Start development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

### Login
- Navigate to `http://localhost:3000/login`
- Use credentials: `admin` / `admin123`

### Dashboard
- View device statistics
- See recent devices
- Navigate to specific device types

### Device Management
- Click on sidebar items to manage different device types
- View device details including status, capacity, charge levels
- Admin users can manage users

## API Integration

The frontend integrates with the Django REST API:

### Authentication
- `POST /api/auth/token/` - Get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token

### Devices
- `GET /api/devices/` - List all devices
- `GET /api/devices/stats/` - Get device statistics
- `GET /api/devices/{id}/` - Get device details

### Device Types
Each device type has full CRUD endpoints:
- `/api/batteries/`
- `/api/electric-vehicles/`
- `/api/solar-panels/`
- `/api/generators/`
- `/api/air-conditioners/`
- `/api/heaters/`

### Users (Admin only)
- `GET /api/users/` - List users
- `GET /api/users/me/` - Get current user
- `POST /api/users/` - Create user
- `PATCH /api/users/{id}/` - Update user

## Docker

The frontend includes a Dockerfile for containerized deployment:

```bash
# Build
docker build -t daylight-frontend .

# Run
docker run -p 3000:3000 daylight-frontend
```

Or use Docker Compose:

```bash
docker-compose up frontend
```

## Testing

The backend API has been tested and verified:

```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test device stats (with token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/devices/stats/
```

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **CSS-in-JS** - Inline styling for components

## Backend Integration

This frontend is designed to work with the Daylight Django backend:

- Django 5.1.4
- Django REST Framework 3.15.2
- Simple JWT 5.3.1
- Django CORS Headers 4.6.0

Backend features:
- JWT authentication endpoints
- RESTful API for all device types
- User management
- Device statistics
- CORS enabled for frontend communication

## Development

### Adding New Device Types

1. Add type definition in `src/types/index.ts`
2. Add API service in `src/api/services.ts`
3. Create page component in `src/pages/`
4. Add route in `src/App.tsx`
5. Add navigation item in `src/components/Layout.tsx`

### Customizing Styles

The application uses inline CSS-in-JS for styling. To customize:
- Edit `styles` objects in component files
- Modify `src/index.css` for global styles
- Update gradient colors in `Login.tsx` and `Dashboard.tsx`

## Troubleshooting

### CORS Issues
Ensure Django backend has CORS configured:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

### Authentication Errors
- Check that backend JWT settings match frontend
- Verify token expiry times
- Check localStorage for stored tokens

### API Connection Issues
- Verify backend is running on port 8000
- Check `.env` file for correct API_BASE_URL
- Ensure CORS headers are set correctly

## Next Steps

Potential enhancements:
- [ ] Add real-time device monitoring with WebSockets
- [ ] Implement device CRUD operations (Create/Update/Delete)
- [ ] Add data visualization charts
- [ ] Implement filtering and sorting
- [ ] Add pagination for large datasets
- [ ] Implement dark mode
- [ ] Add toast notifications
- [ ] Implement form validation
- [ ] Add unit tests
- [ ] Add E2E tests

## License

Part of the Daylight Energy Management System project.
