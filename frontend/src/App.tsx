import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Batteries from './pages/Batteries';
import Users from './pages/Users';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Loading...</p>
      </div>
    );
  }

  return isAuthenticated ? <Layout>{children}</Layout> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/batteries"
            element={
              <ProtectedRoute>
                <Batteries />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute>
                <Users />
              </ProtectedRoute>
            }
          />
          <Route
            path="/electric-vehicles"
            element={
              <ProtectedRoute>
                <div style={{ padding: '24px' }}>
                  <h1>🚗 Electric Vehicles</h1>
                  <p>EV management coming soon...</p>
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/solar-panels"
            element={
              <ProtectedRoute>
                <div style={{ padding: '24px' }}>
                  <h1>☀️ Solar Panels</h1>
                  <p>Solar panel management coming soon...</p>
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/generators"
            element={
              <ProtectedRoute>
                <div style={{ padding: '24px' }}>
                  <h1>⚡ Generators</h1>
                  <p>Generator management coming soon...</p>
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/air-conditioners"
            element={
              <ProtectedRoute>
                <div style={{ padding: '24px' }}>
                  <h1>❄️ Air Conditioners</h1>
                  <p>AC management coming soon...</p>
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/heaters"
            element={
              <ProtectedRoute>
                <div style={{ padding: '24px' }}>
                  <h1>🔥 Heaters</h1>
                  <p>Heater management coming soon...</p>
                </div>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    gap: '16px',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
};

export default App;
