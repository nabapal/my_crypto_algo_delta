#!/bin/bash

# Render.com startup script
echo "🚀 Starting Crypto Trading Bot on Render.com..."

# Install dependencies (if not cached)
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs reports data

# Set environment variables for Render
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_PORT=${PORT:-8501}

# Start the Streamlit dashboard
echo "📊 Launching Streamlit Dashboard on port ${PORT:-8501}..."
exec streamlit run ui/trading_dashboard.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
