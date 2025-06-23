#!/usr/bin/env python3
"""
Script to run Celery worker and beat processes for the Celebrant Portal
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def check_redis():
    """Check if Redis is running."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis is not running: {e}")
        print("Please start Redis with: brew services start redis (Mac) or sudo systemctl start redis (Linux)")
        return False

def run_worker():
    """Run Celery worker."""
    print("🚀 Starting Celery worker...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir)
    
    # Run celery worker
    cmd = [
        'celery', '-A', 'celery_app.celery', 
        'worker', 
        '--loglevel=info',
        '--concurrency=2',
        '--pool=solo' if sys.platform == 'win32' else '--pool=prefork'
    ]
    
    return subprocess.Popen(cmd, env=env)

def run_beat():
    """Run Celery beat scheduler."""
    print("⏰ Starting Celery beat scheduler...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir)
    
    # Run celery beat
    cmd = [
        'celery', '-A', 'celery_app.celery', 
        'beat', 
        '--loglevel=info'
    ]
    
    return subprocess.Popen(cmd, env=env)

def run_flower():
    """Run Celery flower monitoring (optional)."""
    print("🌸 Starting Celery flower monitoring...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir)
    
    # Run celery flower
    cmd = [
        'celery', '-A', 'celery_app.celery', 
        'flower', 
        '--port=5555'
    ]
    
    return subprocess.Popen(cmd, env=env)

def main():
    """Main function to orchestrate Celery processes."""
    print("🎯 Celebrant Portal - Legal Forms Automation")
    print("=" * 50)
    
    # Check Redis
    if not check_redis():
        sys.exit(1)
    
    processes = []
    
    try:
        # Start worker
        worker_process = run_worker()
        processes.append(('worker', worker_process))
        time.sleep(2)  # Give worker time to start
        
        # Start beat scheduler
        beat_process = run_beat()
        processes.append(('beat', beat_process))
        time.sleep(2)  # Give beat time to start
        
        # Optionally start flower monitoring
        start_flower = input("Start Celery Flower monitoring? (y/N): ").lower().strip() == 'y'
        if start_flower:
            try:
                flower_process = run_flower()
                processes.append(('flower', flower_process))
                print("📊 Flower monitoring available at: http://localhost:5555")
            except FileNotFoundError:
                print("⚠️  Flower not installed. Install with: pip install flower")
        
        print("\n✅ All Celery processes started successfully!")
        print("\nActive processes:")
        for name, process in processes:
            print(f"  • {name.capitalize()}: PID {process.pid}")
        
        print("\n📋 Legal Forms Automation Features:")
        print("  • Hourly deadline checks")
        print("  • Daily reminder emails")
        print("  • Weekly compliance reports")
        print("  • Automated form initialization")
        print("  • Alert cleanup")
        
        print("\n🔧 To stop all processes, press Ctrl+C")
        print("=" * 50)
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name.capitalize()} process died with code {process.returncode}")
                    return
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Celery processes...")
        
        # Gracefully terminate processes
        for name, process in processes:
            print(f"  • Stopping {name}...")
            process.terminate()
        
        # Wait for processes to terminate
        for name, process in processes:
            try:
                process.wait(timeout=10)
                print(f"  ✅ {name.capitalize()} stopped")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Force killing {name}...")
                process.kill()
                process.wait()
        
        print("✅ All processes stopped successfully")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        # Clean up processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        sys.exit(1)

if __name__ == '__main__':
    main() 