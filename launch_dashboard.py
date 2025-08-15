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
        print("📊 Dashboard running on port 8501")
        print("🔴 Press Ctrl+C to stop the dashboard")
        print("="*60)
        
        # For cloud deployment, bind to all interfaces
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8501))
        
        # Launch Streamlit with cloud-friendly settings
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.address", host,
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🔴 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    launch_dashboard()
