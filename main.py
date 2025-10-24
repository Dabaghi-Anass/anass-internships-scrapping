import schedule
import time
import subprocess
import threading
from datetime import datetime

def run_scraper():
    print(f"[{datetime.now()}] Running LinkedIn scraper...")
    try:
        subprocess.run(["python", "linkedin.py"], check=True)
        print(f"[{datetime.now()}] Scraper completed successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Scraper failed: {e}")

def run_scheduler():
    run_scraper()
    # Schedule to run every 2 hours
    schedule.every(2).hours.do(run_scraper)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_server():
    import uvicorn
    from server import app
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    run_server()