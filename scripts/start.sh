#!/bin/bash

# Startup script for Fly.io deployment
echo "🚀 Starting Crypto Trading Bot on Fly.io..."

# Create necessary directories
mkdir -p logs reports data

# Set environment variables for production
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Start the dashboard
echo "📊 Launching Streamlit Dashboard..."
exec python launch_dashboard.py
