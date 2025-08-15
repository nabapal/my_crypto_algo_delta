"""
Crypto Trading Bot Dashboard Launcher
Simple script to launch the Streamlit dashboard
"""

import subprocess
import sys
import os

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    try:
        # Get the directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_path = os.path.join(current_dir, "ui", "trading_dashboard.py")
        
        print("🚀 Starting Crypto Trading Bot Dashboard...")
        print("📊 Dashboard will open in your browser at http://localhost:8501")
        print("🔴 Press Ctrl+C to stop the dashboard")
        print("="*60)
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {str(e)}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    launch_dashboard()
