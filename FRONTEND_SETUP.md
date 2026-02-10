# 🚀 Frontend Setup Guide

## Quick Start

### Prerequisites
- Django project running
- PostgreSQL database
- Redis server
- Static files configuration

### Installation Steps

#### 1. Verify Directory Structure

Ensure you have the following structure:

```
Daylight/
├── static/
│   ├── css/
│   │   ├── design-system.css
│   │   ├── components.css
│   │   ├── dashboard.css
│   │   └── admin-custom.css
│   └── js/
│       ├── dashboard.js
│       └── energy-viz.js
├── templates/
│   ├── dashboard.html
│   └── admin/
│       └── base_site.html
└── apps/
    └── devices/
        └── views.py
```

#### 2. Settings Configuration

Verify `config/settings/base.py` has:

```python
# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ Templates directory
        'APP_DIRS': True,
        # ...
    },
]

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # ✅ Static files directory
]
```

#### 3. URL Configuration

Verify `config/urls.py` includes:

```python
from apps.devices.views import dashboard, dashboard_demo

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard_main'),
    path('demo/', dashboard_demo, name='dashboard_demo'),
    path('admin/', admin.site.urls),
    # ...
]
```

#### 4. Collect Static Files

Run this command to collect all static files:

```bash
python manage.py collectstatic --noinput
```

#### 5. Start the Server

```bash
python manage.py runserver
```

### Access Points

Once running, access these URLs:

| URL | Description | Auth Required |
|-----|-------------|---------------|
| `http://localhost:8000/` | Main Dashboard | Yes |
| `http://localhost:8000/demo/` | Demo Dashboard | No |
| `http://localhost:8000/admin/` | Admin Panel | Yes |
| `http://localhost:8000/graphql/` | GraphQL Playground | No |

## 🎨 Preview

### Dashboard Features

#### Energy Overview Section
- **Total Production**: Real-time wattage from solar panels and generators
- **Total Consumption**: Current energy usage across all devices
- **Storage Level**: Battery charge percentage and capacity
- **Net Grid Flow**: Import/export balance

#### Energy Flow Visualization
- Visual diagram showing energy movement
- Production sources on left (solar, generators)
- Home center showing net flow
- Consumption & storage on right (HVAC, batteries, EVs)

#### Connected Devices Grid
- Dynamic cards for each device
- Device type icons and status badges
- Real-time specifications
- Storage visualization for batteries/EVs

### Admin Panel Features
- Custom Daylight Energy branding
- Aurora background theme
- Glassmorphism card design
- Enhanced table styling
- Energy-colored status messages

## 🧪 Testing

### Test Dashboard Rendering

1. **Check Static Files Loading**:
   - Open browser DevTools (F12)
   - Go to Network tab
   - Refresh dashboard
   - Verify CSS and JS files load with 200 status

2. **Test GraphQL Integration**:
   ```bash
   # Open GraphQL playground
   http://localhost:8000/graphql/

   # Test energy stats query
   query {
     energyStats {
       currentProduction
       currentConsumption
       currentStorage {
         percentage
       }
     }
   }
   ```

3. **Test Responsive Design**:
   - Open DevTools responsive mode
   - Test mobile (375px)
   - Test tablet (768px)
   - Test desktop (1920px)

### Test Admin Customization

1. Navigate to: `http://localhost:8000/admin/`
2. Verify custom styling:
   - ✅ Gradient header with "Daylight Energy" branding
   - ✅ Aurora background animation
   - ✅ Glassmorphism cards
   - ✅ Custom table styling
   - ✅ Energy-themed colors

## 🎯 Customization

### Change Brand Colors

Edit `static/css/design-system.css`:

```css
:root {
  /* Primary energy colors */
  --color-energy-production: #00ff88;   /* Green for production */
  --color-energy-consumption: #ff8c42;  /* Orange for consumption */
  --color-energy-storage: #00d4ff;      /* Cyan for storage */
}
```

### Modify Dashboard Layout

Edit `templates/dashboard.html` to:
- Rearrange sections
- Add new components
- Change grid layouts

### Customize Admin

Edit `static/css/admin-custom.css` for:
- Different color schemes
- Layout adjustments
- Custom branding elements

## 📊 Data Integration

### GraphQL Queries Used

#### Energy Stats
```graphql
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
```

#### All Devices
```graphql
query {
  allDevices {
    id
    name
    deviceType
    status
    # Type-specific fields...
  }
}
```

### Auto-Refresh Configuration

Edit `static/js/dashboard.js`:

```javascript
const CONFIG = {
  graphqlEndpoint: '/graphql/',
  refreshInterval: 5000,  // Change refresh rate (milliseconds)
  maxRetries: 3,
  animationDuration: 500
};
```

## 🐛 Common Issues

### Issue: Styles Not Loading

**Symptoms**: Dashboard appears unstyled, default HTML rendering

**Solutions**:
1. Check static files configuration in settings
2. Run `python manage.py collectstatic`
3. Verify static files directory exists
4. Clear browser cache (Ctrl+Shift+R)
5. Check browser console for 404 errors

### Issue: Dashboard Shows 404

**Symptoms**: Dashboard URL returns "Page not found"

**Solutions**:
1. Verify `apps/devices/views.py` exists
2. Check URL patterns in `config/urls.py`
3. Ensure views are imported correctly
4. Check for typos in URL paths

### Issue: GraphQL Data Not Loading

**Symptoms**: Dashboard loads but shows "0" for all values

**Solutions**:
1. Verify GraphQL endpoint is running: `http://localhost:8000/graphql/`
2. Check database has devices and energy data
3. Run simulation task: `python manage.py shell` → trigger simulation
4. Check browser console for JavaScript errors
5. Verify CORS settings if applicable

### Issue: Admin Styles Not Applied

**Symptoms**: Admin looks like default Django admin

**Solutions**:
1. Verify `templates/admin/base_site.html` exists
2. Check template directory is configured in settings
3. Clear browser cache
4. Ensure CSS file paths are correct
5. Check static files are collected

## 🔄 Development Workflow

### Making Style Changes

1. Edit CSS files in `static/css/`
2. Refresh browser (Ctrl+R)
3. If changes don't appear:
   - Hard refresh (Ctrl+Shift+R)
   - Clear cache
   - Run collectstatic again

### Making Template Changes

1. Edit HTML files in `templates/`
2. Save file
3. Refresh browser
4. No collectstatic needed for template changes

### Making JavaScript Changes

1. Edit JS files in `static/js/`
2. Save file
3. Hard refresh browser (Ctrl+Shift+R) to bypass cache
4. Check console for errors

## 📈 Performance Tips

### Optimize Static Files

1. **Minify CSS/JS** (production):
   ```bash
   # Install minifier
   pip install django-compressor

   # Configure in settings
   COMPRESS_ENABLED = True
   ```

2. **Enable Caching**:
   ```python
   # settings.py
   STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
   ```

3. **Use CDN** (production):
   - Upload static files to CDN
   - Update `STATIC_URL` to CDN URL

### Dashboard Performance

- Auto-refresh runs every 5 seconds
- Devices only re-fetch occasionally (20% chance)
- Animations use CSS when possible (GPU accelerated)
- No heavy libraries (vanilla JS)

## 🎓 Next Steps

### Recommended Enhancements

1. **Add Real-time WebSockets**:
   - Install Django Channels
   - Replace polling with WebSocket updates
   - Reduce server load

2. **Add Charts**:
   - Install Chart.js or D3.js
   - Create historical energy graphs
   - Add trend analysis

3. **Progressive Web App**:
   - Add service worker
   - Enable offline mode
   - Install as mobile app

4. **User Preferences**:
   - Dark/light theme toggle
   - Dashboard layout customization
   - Auto-refresh interval settings

5. **Notifications**:
   - Alert on high consumption
   - Battery low warnings
   - Device offline notifications

## 📚 Additional Resources

- [Django Static Files Documentation](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)
- [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

## 🆘 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review browser console for errors
3. Check Django logs for server errors
4. Verify all dependencies are installed
5. Ensure database migrations are applied

---

**Happy coding! ⚡**
