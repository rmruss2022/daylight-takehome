import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/batteries', label: 'Batteries', icon: '🔋' },
    { path: '/electric-vehicles', label: 'EVs', icon: '🚗' },
    { path: '/solar-panels', label: 'Solar Panels', icon: '☀️' },
    { path: '/generators', label: 'Generators', icon: '⚡' },
    { path: '/air-conditioners', label: 'AC Units', icon: '❄️' },
    { path: '/heaters', label: 'Heaters', icon: '🔥' },
  ];

  if (user?.is_staff) {
    navItems.push({ path: '/users', label: 'Users', icon: '👥' });
  }

  return (
    <div style={styles.container}>
      <nav style={styles.sidebar}>
        <div style={styles.brand}>
          <h2 style={styles.brandText}>⚡ Daylight</h2>
          <p style={styles.brandSubtext}>Energy Manager</p>
        </div>
        
        <div style={styles.nav}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                ...styles.navItem,
                ...(isActive(item.path) ? styles.navItemActive : {}),
              }}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        <div style={styles.userSection}>
          <div style={styles.userInfo}>
            <div style={styles.userAvatar}>
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={styles.userName}>{user?.username}</div>
              <div style={styles.userRole}>
                {user?.is_staff ? 'Admin' : 'User'}
              </div>
            </div>
          </div>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </nav>

      <main style={styles.main}>
        <div style={styles.content}>{children}</div>
      </main>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    background: '#f5f7fa',
  },
  sidebar: {
    width: '260px',
    background: 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
    color: 'white',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '4px 0 12px rgba(0, 0, 0, 0.1)',
  },
  brand: {
    padding: '24px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  brandText: {
    margin: '0 0 4px 0',
    fontSize: '24px',
    fontWeight: 'bold',
  },
  brandSubtext: {
    margin: 0,
    fontSize: '12px',
    opacity: 0.7,
  },
  nav: {
    flex: 1,
    padding: '16px 0',
    overflowY: 'auto',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '12px 24px',
    color: 'rgba(255, 255, 255, 0.7)',
    textDecoration: 'none',
    transition: 'all 0.2s',
    cursor: 'pointer',
  },
  navItemActive: {
    background: 'rgba(102, 126, 234, 0.3)',
    color: 'white',
    borderLeft: '4px solid #667eea',
  },
  navIcon: {
    marginRight: '12px',
    fontSize: '20px',
  },
  userSection: {
    padding: '16px',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  userAvatar: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#667eea',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
    fontWeight: 'bold',
  },
  userName: {
    fontSize: '14px',
    fontWeight: '600',
  },
  userRole: {
    fontSize: '12px',
    opacity: 0.7,
  },
  logoutButton: {
    width: '100%',
    padding: '10px',
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s',
  },
  main: {
    flex: 1,
    overflowY: 'auto',
  },
  content: {
    minHeight: '100%',
  },
};

export default Layout;
