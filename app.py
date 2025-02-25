from flask import Flask, request, abort
import threading
import time
from dotenv import load_dotenv
import psutil,os
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

try:
    load_dotenv()
except Exception as e:
    print(f"Error loading .env file: {e}")

app = Flask(__name__)

# Prometheus Metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')

def monitor_cpu_usage():
    while True:
        try:
            usage = psutil.cpu_percent()
            cpu_usage.set(usage)
            print(f"CPU Usage Updated: {usage}%")
        except Exception as e:
            print(f"Error in monitoring thread: {e}")
            time.sleep(5)  

@app.route('/')
def home():
    return "Flask CPU Metrics App Running!"

@app.route('/metrics')
def metrics():
    try:
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        return str(e), 500

def main():
    monitor_thread = threading.Thread(target=monitor_cpu_usage, daemon=True)
    monitor_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()