# 🚀 Deploy to Render.com - Step by Step Guide

## 🌟 Why Render.com?
- ✅ **Free Tier**: 750 hours/month free (enough for 24/7)
- ✅ **No Credit Card Required**: Unlike Fly.io
- ✅ **Easy Deployment**: Direct from GitHub
- ✅ **Auto-Deploy**: Updates automatically from your repo

## 📋 Quick Deployment Steps

### Step 1: Connect GitHub Repository
1. Go to [Render.com](https://render.com)
2. Sign up with your GitHub account
3. Click "New +" → "Web Service"
4. Connect your repository: `nabapal/my_crypto_algo_delta`

### Step 2: Configure Service
```
Name: crypto-trading-bot
Region: Singapore (closest to India)
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run ui/trading_dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
```

### Step 3: Environment Variables (Optional)
Add these in Render dashboard:
```
STREAMLIT_SERVER_HEADLESS = true
STREAMLIT_SERVER_ENABLE_CORS = false
PYTHON_VERSION = 3.11.0
```

### Step 4: Deploy! 🚀
- Click "Create Web Service"
- Render will automatically build and deploy
- Your app will be live at: `https://crypto-trading-bot-XXXX.onrender.com`

## 🎯 What You'll Get

### ✅ Full Dashboard Access
- Real-time trading monitoring
- Strategy configuration (v1, v2, v3)
- Paper trading controls
- Performance analytics

### ✅ Free Tier Benefits
- **750 hours/month**: Enough for 24/7 operation
- **512MB RAM**: Sufficient for the bot
- **Auto-sleep**: Spins down after 15min inactivity (saves hours)
- **Custom domain**: Available on free tier

### ✅ Auto-Deploy
- Push to GitHub → Automatically deploys to Render
- No manual deployment needed

## 🔧 Render.com Optimizations Applied

1. **Streamlit Configuration**: Optimized for web deployment
2. **Health Checks**: Built-in endpoint monitoring
3. **Environment Variables**: Production-ready settings
4. **Requirements**: Pinned versions for stability
5. **Start Command**: Optimized for Render's infrastructure

## 💡 Pro Tips

### Keep Your App Awake (Optional)
Free tier apps sleep after 15min inactivity. To keep awake:
1. Use a service like [UptimeRobot](https://uptimerobot.com)
2. Ping your app every 10 minutes

### Monitor Usage
- Check your service hours in Render dashboard
- Free tier: 750 hours/month
- Upgrade if needed for 24/7 operation

## 🎊 Expected Deployment Time
- **Build Time**: 2-3 minutes
- **First Deploy**: 3-5 minutes
- **Subsequent Deploys**: 1-2 minutes

Your crypto trading bot will be live and accessible worldwide! 🌍
