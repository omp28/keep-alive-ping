import ssl
print(ssl.OPENSSL_VERSION)
import random
import time
from datetime import datetime
from flask import Flask, jsonify
import requests
import threading
import logging
import os
import sys



# Configure logging
log_file_path = "api_monitor.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Flask app for hosting the API
app = Flask(__name__)

# API configurations
APIS = [
    {
        "name": "Pipeline Parse API",
        "url": "https://vectorshift-backend-ze4i.onrender.com/pipelines/parse",
        "method": "POST",
        "data": {
            "nodes": [
                {"id": "customOutput-1", "type": "customOutput", "position": {}, "data": {}},
                {"id": "text-1", "type": "text", "position": {}, "data": {}},
                {"id": "logger-1", "type": "logger", "position": {}, "data": {}}
            ],
            "edges": [
                {"id": "reactflow__edge-text-1text-1-output-0-customOutput-1customOutput-1-input-0",
                 "source": "text-1", "target": "customOutput-1", "sourceHandle": "text-1-output-0", "targetHandle": "customOutput-1-input-0"},
                {"id": "reactflow__edge-text-1text-1-output-0-logger-1logger-1-input-0",
                 "source": "text-1", "target": "logger-1", "sourceHandle": "text-1-output-0", "targetHandle": "logger-1-input-0"}
            ]
        }
    },
    {
        "name": "Marketplace Men API",
        "url": "https://marketplace.omp28.me/_next/data/A69ycs2melZjH8welEB84/men.json",
        "method": "GET"
    },
    {
        "name": "Marketplace Women API",
        "url": "https://marketplace.omp28.me/_next/data/A69ycs2melZjH8welEB84/women.json",
        "method": "GET"
    },
    {
        "name": "QuickChat Login API",
        "url": "https://quickchat-m4ji.onrender.com/api/user/login",
        "method": "POST",
        "data": {
            "email": "dummy@example.com",  # Replace with actual email
            "password": "password123"      # Replace with actual password
        }
    }
]

# Helper function to log API responses
def log_api_response(name, status_code):
    """Log API response details."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"{name} - Status: {status_code} - Time: {timestamp}")

# Thread function to ping APIs
# Thread function to ping APIs
def ping_apis_without_overlap():
    while True:
        for api in APIS:
            try:
                if api["method"] == "POST":
                    response = requests.post(api["url"], json=api.get("data", {}))
                else:
                    response = requests.get(api["url"])
                log_api_response(api["name"], response.status_code)
            except requests.exceptions.RequestException as e:
                log_api_response(api["name"], f"Error: {str(e)}")
            
            # Random interval between 0 to 180 seconds before next API ping
            random_interval = random.randint(0, 180)
            time.sleep(random_interval)


# Flask route to fetch logs
@app.route("/logs", methods=["GET"])
def get_logs():
    """Retrieve the last 50 lines from the log file."""
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()[-50:]  # Fetch the last 50 lines
        return jsonify({"logs": lines})
    except FileNotFoundError:
        return jsonify({"error": "Log file not found"}), 404

# Daemonize the process
def daemonize():
    if os.fork() > 0:
        sys.exit()

    os.setsid()
    if os.fork() > 0:
        sys.exit()

    # Redirect standard file descriptors to /dev/null
    sys.stdout = open("/dev/null", "w")
    sys.stderr = open("/dev/null", "w")
    sys.stdin = open("/dev/null", "r")

# Main logic
if __name__ == "__main__":
    # Daemonize the process
    daemonize()

    # Start thread to ping APIs
    threading.Thread(target=ping_apis_without_overlap, daemon=True).start()

    # Run Flask app
    app.run(host="0.0.0.0", port=5001)
