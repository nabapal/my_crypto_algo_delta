"""
FastAPI Dashboard Launcher
Starts the web dashboard for crypto trading bot monitoring
"""

import os
import sys
import subprocess
import time

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", 
            "web_dashboard/requirements.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def start_dashboard():
    """Start the FastAPI dashboard"""
    print("🚀 Starting FastAPI Trading Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔴 Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Change to web_dashboard directory
        os.chdir("web_dashboard")
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n🔴 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    print("🤖 FastAPI Trading Dashboard Launcher")
    print("=" * 60)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI packages found")
    except ImportError:
        print("📦 Installing missing packages...")
        if not install_requirements():
            print("❌ Failed to install requirements. Exiting.")
            sys.exit(1)
    
    # Start dashboard
    start_dashboard()
