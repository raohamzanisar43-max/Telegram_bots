# Railway Deployment Guide - Profitability Intelligence

## 🚀 Quick Deploy to Railway

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected to Railway
- All environment variables configured

### Step 1: Connect Repository
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository: `raohamzanisar43-max/Telegram_bots`
4. Railway will automatically detect the Python project

### Step 2: Configure Environment Variables
In Railway Dashboard → Settings → Variables, add:

```bash
# Telegram Bot Tokens
SIGNALS_BOT_TOKEN=8789501428:AAHJKgfD_lxl30oS0a06v9qDRTGcmmG-u7U
COPY_BOT_TOKEN=8705346390:AAEng-RwtoPtbm8QULWu0z1FNiALsVvBcnE
FUNDED_BOT_TOKEN=8696214640:AAEaNIrHR2wKHNiibJ8UzAnZ7hhLLlQg23U

# Database (Railway PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=profitability
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_railway_db_password

# Redis (Railway Redis)
REDIS_HOST=localhost
REDIS_PORT=6379

# MetaAPI (if using MT4 integration)
META_API_TOKEN=your_metaapi_token
MT4_ACCOUNT_ID=your_mt4_account_id

# Admin
ADMIN_SECRET=your_strong_admin_secret

# VIP Channel
SIGNALS_VIP_CHANNEL_ID=-1001234567890

# General
LOG_LEVEL=INFO
TZ=UTC
PORT=4000
PYTHONPATH=.
```

### Step 3: Add Railway Services
1. Click "New Service" → "Add PostgreSQL"
2. Click "New Service" → "Add Redis"
3. Update environment variables with Railway service URLs

### Step 4: Deploy
- Railway will automatically deploy on each push to main branch
- Monitor deployment logs in Railway Dashboard

### Step 5: Verify Deployment
1. Check Railway logs for successful startup
2. Test Admin API: `https://your-app.railway.app/health`
3. Test Telegram bots by sending `/start`

## 📋 Deployment Files Created

### `main.py` - Single Entry Point
- Starts all three bots concurrently
- Professional logging and error handling
- Railway-compatible configuration
- Graceful shutdown support

### `Procfile` - Railway Process Definition
```procfile
web: python main.py
```

### `requirements.txt` - Dependencies
- All required packages for Railway deployment
- Optimized versions for compatibility

### `railway.toml` - Railway Configuration
- Health check endpoint
- Restart policies
- Service configuration

## 🔧 Local Testing

```bash
# Test locally before deploying
python main.py
```

## 🌐 Production URLs

After deployment, your services will be available at:
- **Admin API**: `https://your-app.railway.app/`
- **Health Check**: `https://your-app.railway.app/health`
- **Telegram Bots**: Same bot usernames, running on Railway infrastructure

## 📊 Monitoring

- Railway Dashboard for deployment logs
- Admin API health endpoint for service status
- Telegram bot responses for functionality testing

## 🛠️ Troubleshooting

### Common Issues:
1. **Environment Variables**: Ensure all required variables are set
2. **Database Connection**: Verify PostgreSQL service is running
3. **Bot Tokens**: Double-check token validity
4. **Port Configuration**: Railway uses PORT environment variable

### Debug Commands:
```bash
# Check logs in Railway Dashboard
# Test locally with same environment variables
# Verify bot tokens via Telegram API
```

## ✅ Success Indicators

- ✅ All three bots respond to `/start`
- ✅ Admin API returns health status
- ✅ Railway deployment shows "Running"
- ✅ No error logs in Railway Dashboard

## 🎯 Professional Features

- **Single Entry Point**: Easy deployment and management
- **Concurrent Execution**: All bots run simultaneously
- **Graceful Shutdown**: Clean service termination
- **Health Monitoring**: Built-in health checks
- **Professional Logging**: Structured logs for debugging
- **Railway Optimized**: Configured for cloud deployment

Your professional trading bot system is now ready for Railway deployment! 🚀
