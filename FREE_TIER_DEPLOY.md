# Free Tier Deployment Guide for Fly.io

## 🆓 Using Your 3 Free Shared-CPU VMs

### Step 1: Add Payment Method
Even for free tier, Fly.io requires a payment method for verification:
1. Go to https://fly.io/dashboard/nabapal-pal-gmail-com/billing
2. Add a credit card (you won't be charged for free tier usage)

### Step 2: Deploy with Free Tier Configuration
```bash
# Create and deploy the app
flyctl apps create my-crypto-algo-delta
flyctl deploy

# Your app will use:
# - 1 shared-CPU VM
# - 512MB RAM (free tier optimized)
# - Mumbai region (bom)
```

### Step 3: Monitor Free Tier Usage
```bash
# Check your app status
flyctl status

# View logs
flyctl logs

# Monitor resource usage
flyctl scale show
```

## 🔧 Free Tier Optimizations Applied

1. **Memory**: Reduced to 512MB (within free limits)
2. **CPU**: 1 shared-CPU core
3. **Auto-scaling**: Disabled to control costs
4. **Health checks**: Optimized intervals
5. **Dependencies**: Minimal installation

## 💰 Cost Breakdown
- **Shared-CPU VM**: FREE (up to 3 VMs)
- **256MB RAM**: FREE allowance
- **Additional 256MB**: Still within generous free tier
- **Bandwidth**: 100GB/month FREE

## 🚀 Expected Performance
- **Dashboard**: Fully functional
- **Paper Trading**: Real-time monitoring
- **Strategy Switching**: All versions (v1, v2, v3)
- **Session Management**: Complete logging

Your trading bot will run 24/7 on Fly.io's free tier! 🎉
