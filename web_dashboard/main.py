"""
FastAPI Trading Dashboard - Main Application
Real-time monitoring for crypto trading bot with WebSocket updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
from typing import List
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.trading_data import TradingDataManager
from api.websocket_manager import ConnectionManager
from models import CleanTradingDataManager

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Trading Bot Dashboard",
    description="Real-time monitoring and control for paper trading bot",
    version="1.0.0"
)

# Mount static files
# Mount static files with correct path
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: Static directory not found at {static_dir}")
    # Create a minimal static directory structure
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize managers
trading_data = TradingDataManager()
clean_trading_data = CleanTradingDataManager()
websocket_manager = ConnectionManager()

# Import bot integration
from models.bot_integration import BotDataIntegration
bot_integration = BotDataIntegration()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    context = {
        "request": request,
        "title": "Crypto Trading Bot Dashboard"
    }
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/api/bot-integrated")
async def get_bot_integrated_data():
    """Get data directly from bot integration (NEW APPROACH)"""
    return await bot_integration.get_bot_live_data()

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data structure using clean implementation"""
    dashboard_data = await clean_trading_data.get_dashboard_data()
    return dashboard_data.to_dict()

@app.get("/api/status")
async def get_status():
    """Get comprehensive bot and financial status (legacy endpoint)"""
    return await trading_data.get_comprehensive_status()

@app.get("/api/trades")
async def get_trades():
    """Get trading history"""
    return await trading_data.get_trades_data()

@app.get("/api/performance")
async def get_performance():
    """Get performance metrics"""
    return await trading_data.get_performance_data()

@app.get("/api/logs/{log_type}")
async def get_logs(log_type: str):
    """Get specific log type"""
    return await trading_data.get_log_data(log_type)

@app.websocket("/ws/trading-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    
    # Send initial status
    initial_status = await trading_data.get_current_status()
    await websocket.send_json(initial_status)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "heartbeat", "status": "alive"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Background task to monitor trading changes
@app.on_event("startup")
async def startup_event():
    """Start background monitoring tasks"""
    print("🚀 Starting FastAPI Trading Dashboard...")
    print("📊 Initializing trading data monitoring...")
    
    # Start file monitoring
    asyncio.create_task(trading_data.start_monitoring(websocket_manager))
    
    print("✅ Dashboard ready!")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
