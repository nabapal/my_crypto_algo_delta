"""
Bot API Routes
Clean API routes that directly integrate with the paper trading bot
"""

from fastapi import APIRouter
from models.bot_integration import BotDataIntegration

router = APIRouter()
bot_integration = BotDataIntegration()

@router.get("/bot/status")
async def get_bot_status():
    """
    Get comprehensive bot status using direct bot integration
    This replaces the old log parsing approach with proper bot integration
    """
    return await bot_integration.get_bot_live_data()

@router.get("/bot/portfolio")
async def get_bot_portfolio():
    """Get detailed portfolio information"""
    data = await bot_integration.get_bot_live_data()
    return data["portfolio"]

@router.get("/bot/position")
async def get_bot_position():
    """Get active position information"""
    data = await bot_integration.get_bot_live_data()
    return data["active_position"]

@router.get("/bot/stats")
async def get_bot_stats():
    """Get trading statistics"""
    data = await bot_integration.get_bot_live_data()
    return data["trading_stats"]
