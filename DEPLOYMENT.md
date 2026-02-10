# Deployment Guide

## Quick Deploy to Railway

### Option 1: One-Click Deploy (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rmruss2022/daylight-takehome)

Click the button above and Railway will:
- Create a new project
- Set up PostgreSQL and Redis automatically
- Deploy the Django web server
- Deploy Celery worker and beat services
- Provide a public URL

### Option 2: CLI Deployment

```bash
# Install Railway CLI (if not already installed)
brew install railway
# or
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd daylight-takehome
railway init

# Link GitHub repo (optional - for auto-deploys)
railway link

# Create PostgreSQL service
railway add --database=postgresql

# Create Redis service  
railway add --database=redis

# Set environment variables
railway variables set DEBUG=False
railway variables set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
railway variables set DJANGO_SUPERUSER_USERNAME=admin
railway variables set DJANGO_SUPERUSER_PASSWORD=admin123secure
railway variables set DJANGO_SUPERUSER_EMAIL=admin@daylight.example.com

# Deploy
railway up

# Get the public URL
railway domain
```

## Environment Variables

Railway will automatically provide:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `PORT` - Port to bind the application

You need to set:
- `SECRET_KEY` - Django secret key (auto-generated above)
- `DEBUG` - Set to `False` for production
- `DJANGO_SUPERUSER_USERNAME` - Admin username (default: admin)
- `DJANGO_SUPERUSER_PASSWORD` - Admin password  
- `DJANGO_SUPERUSER_EMAIL` - Admin email
- `ALLOWED_HOSTS` - Set to `*` or specific Railway domain
- `JWT_SECRET_KEY` - JWT authentication key (in .env.production)

## Services Required

The application needs these services running:

1. **Web Server** (Django + Gunicorn)
   - Serves the API and dashboard
   - Runs on port 8000 (or Railway's PORT)
   
2. **PostgreSQL Database**
   - Stores device data, users, energy stats
   
3. **Redis Cache**
   - Stores real-time simulation data
   - Used by Celery as message broker

4. **Celery Worker**
   - Processes background tasks
   - Runs device simulations
   - Command: `celery -A config worker --loglevel=info`

5. **Celery Beat**
   - Schedules periodic simulation tasks (every 60 seconds)
   - Command: `celery -A config beat --loglevel=info`

## Post-Deployment Steps

After deployment completes:

1. **Access the application:**
   ```bash
   railway open
   ```

2. **Run migrations** (if not auto-run):
   ```bash
   railway run python manage.py migrate
   ```

3. **Create superuser** (if not auto-created):
   ```bash
   railway run python manage.py createsuperuser --noinput
   ```

4. **Check logs:**
   ```bash
   railway logs
   ```

## Demo Credentials

After deployment, you can login with:

- **Admin Panel:** `/admin/`
  - Username: `admin`
  - Password: `admin123secure` (or your custom password)

- **Dashboard:** `/`
  - Username: `testuser1`
  - Password: `testpass123`

- **React Frontend:** `/frontend/` (port 3000 if separate deployment)

## Architecture

```
┌─────────────────┐
│   Client/User   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Railway CDN    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       Django Web Server             │
│     (Gunicorn + Whitenoise)         │
│                                     │
│  - REST API (/api/)                 │
│  - GraphQL (/graphql/)              │
│  - Django Dashboard (/)             │
│  - Admin Panel (/admin/)            │
└─────────┬─────────┬─────────────────┘
          │         │
          │         │
          ▼         ▼
┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │
│   Database   │  │    Cache     │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Celery Workers    │
              │   - Simulation      │
              │   - Background Jobs │
              └──────────────────────┘
                         ▲
                         │
              ┌──────────┴─────────┐
              │   Celery Beat      │
              │  (Scheduler)       │
              └────────────────────┘
```

## Monitoring

After deployment, monitor your services:

```bash
# View web server logs
railway logs --service=web

# View Celery worker logs  
railway logs --service=celery-worker

# View Celery beat logs
railway logs --service=celery-beat

# Check service status
railway status
```

## Scaling

To handle more traffic:

```bash
# Scale web workers
railway up --replicas=3 --service=web

# Scale Celery workers
railway up --replicas=2 --service=celery-worker
```

## Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL is set
railway variables get DATABASE_URL

# Test connection
railway run python manage.py dbshell
```

### Celery Not Running
```bash
# Check Redis connection
railway variables get REDIS_URL

# Restart Celery services
railway restart --service=celery-worker
railway restart --service=celery-beat
```

### Static Files Not Loading
```bash
# Collect static files manually
railway run python manage.py collectstatic --noinput
```

### Application Errors
```bash
# View detailed logs
railway logs --tail=100

# Check environment variables
railway variables

# SSH into container
railway shell
```

## Alternative Deployment Options

### Render.com
1. Import GitHub repo
2. Create Web Service (uses Dockerfile automatically)
3. Add PostgreSQL database
4. Add Redis instance  
5. Configure environment variables
6. Deploy

### Fly.io
```bash
fly launch
fly postgres create
fly redis create  
fly deploy
```

### Docker Compose (Self-Hosted)
```bash
docker-compose -f docker-compose.yml up -d
```

## Production Checklist

Before going live:

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Set strong `DJANGO_SUPERUSER_PASSWORD`
- [ ] Configure `ALLOWED_HOSTS` with actual domain
- [ ] Enable SSL (`SECURE_SSL_REDIRECT=True`)
- [ ] Set up monitoring and alerting
- [ ] Configure backups for PostgreSQL
- [ ] Set up log aggregation
- [ ] Configure CORS for production frontend URL
- [ ] Review and lock down Django admin access
- [ ] Enable rate limiting on API endpoints
- [ ] Set up CDN for static files (if needed)

## URLs After Deployment

Once deployed, your application will be available at:

- **Dashboard:** `https://your-app-name.railway.app/`
- **Admin:** `https://your-app-name.railway.app/admin/`
- **API:** `https://your-app-name.railway.app/api/`
- **GraphQL:** `https://your-app-name.railway.app/graphql/`
- **API Docs:** `https://your-app-name.railway.app/api/docs/`

## Support

For deployment issues:
- Railway: https://railway.app/help
- GitHub Issues: https://github.com/rmruss2022/daylight-takehome/issues
