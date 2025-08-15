"""
Bot Status Monitor
Real-time monitoring utilities for the trading dashboard
"""

import psutil
import os
import json
import time
from datetime import datetime, timedelta

class BotStatusMonitor:
    def __init__(self):
        self.log_dir = "logs"
        self.reports_dir = "reports"
        
    def is_bot_running(self):
        """Check if trading bot process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'python.exe':
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'paper_trading_bot.py' in cmdline:
                        return True, proc.info['pid']
            return False, None
        except:
            return False, None
    
    def get_last_log_activity(self):
        """Get timestamp of last log activity"""
        try:
            log_files = [
                "trading_activity_20250815.log",
                "market_data_20250815.log",
                "api_communication_20250815.log"
            ]
            
            latest_time = None
            for log_file in log_files:
                log_path = os.path.join(self.log_dir, log_file)
                if os.path.exists(log_path):
                    mod_time = datetime.fromtimestamp(os.path.getmtime(log_path))
                    if latest_time is None or mod_time > latest_time:
                        latest_time = mod_time
            
            return latest_time
        except:
            return None
    
    def get_current_position(self):
        """Get current trading position from latest performance file"""
        try:
            if not os.path.exists(self.reports_dir):
                return None
            
            files = [f for f in os.listdir(self.reports_dir) if f.startswith('performance_detail_')]
            if not files:
                return None
            
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.reports_dir, x)))
            
            with open(os.path.join(self.reports_dir, latest_file), 'r') as f:
                data = json.load(f)
                return data.get('current_position')
        except:
            return None
    
    def get_health_status(self):
        """Get overall bot health status"""
        is_running, pid = self.is_bot_running()
        last_activity = self.get_last_log_activity()
        current_position = self.get_current_position()
        
        # Determine health status
        if not is_running:
            status = "STOPPED"
            health = "🔴"
        elif last_activity and datetime.now() - last_activity < timedelta(minutes=5):
            status = "HEALTHY"
            health = "🟢"
        elif last_activity and datetime.now() - last_activity < timedelta(minutes=15):
            status = "IDLE"
            health = "🟡"
        else:
            status = "UNHEALTHY"
            health = "🔴"
        
        return {
            'status': status,
            'health_icon': health,
            'is_running': is_running,
            'process_id': pid,
            'last_activity': last_activity.isoformat() if last_activity else None,
            'has_position': current_position is not None,
            'position_type': current_position.get('signal_data', {}).get('position_type') if current_position else None
        }
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        except:
            return {}
    
    def get_log_summary(self, lines=10):
        """Get recent log entries summary"""
        try:
            log_files = {
                'trading': "trading_activity_20250815.log",
                'market': "market_data_20250815.log", 
                'errors': "errors_20250815.log"
            }
            
            summary = {}
            for log_type, log_file in log_files.items():
                log_path = os.path.join(self.log_dir, log_file)
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                        summary[log_type] = [line.strip() for line in recent_lines if line.strip()]
                else:
                    summary[log_type] = []
            
            return summary
        except:
            return {}

# Utility functions for dashboard
def format_time_ago(timestamp):
    """Format timestamp as 'X minutes ago'"""
    if not timestamp:
        return "Unknown"
    
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        
        now = datetime.now()
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        
        diff = now - dt
        
        if diff.seconds < 60:
            return f"{diff.seconds} seconds ago"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        elif diff.days == 0:
            return f"{diff.seconds // 3600} hours ago"
        else:
            return f"{diff.days} days ago"
    except:
        return "Unknown"

def get_status_color(status):
    """Get color code for status"""
    colors = {
        'HEALTHY': '#28a745',
        'IDLE': '#ffc107', 
        'UNHEALTHY': '#dc3545',
        'STOPPED': '#6c757d'
    }
    return colors.get(status, '#6c757d')
