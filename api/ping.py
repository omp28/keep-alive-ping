import random
import time
from datetime import datetime
from flask import Flask, jsonify, request
import requests
import threading
from collections import deque

# Flask app for hosting the API
app = Flask(__name__)

# In-memory log storage using deque for thread-safe, fixed-size logs
api_logs = deque(maxlen=20)

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

# Helper function to get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to log API responses
def log_api_response(name, status_code, timestamp):
    log_entry = {
        "name": name,
        "timestamp": timestamp,
        "status_code": status_code
    }
    api_logs.appendleft(log_entry)

# Graceful shutdown mechanism
shutdown_event = threading.Event()

# Shared lock to prevent overlap
api_lock = threading.Lock()

# Function to ping APIs without overlap
def ping_apis_without_overlap():
    while not shutdown_event.is_set():
        for api in APIS:
            with api_lock:  # Ensure only one API is pinged at a time
                try:
                    if api["method"] == "POST":
                        response = requests.post(api["url"], json=api.get("data", {}))
                    else:
                        response = requests.get(api["url"])

                    log_api_response(
                        name=api["name"],
                        status_code=response.status_code,
                        timestamp=get_timestamp()
                    )
                    print(f"{api['name']} - Status: {response.status_code}, Time: {get_timestamp()}")
                except requests.exceptions.Timeout:
                    log_api_response(
                        name=api["name"],
                        status_code="Timeout",
                        timestamp=get_timestamp()
                    )
                    print(f"{api['name']} - Timeout Error, Time: {get_timestamp()}")
                except requests.exceptions.RequestException as e:
                    log_api_response(
                        name=api["name"],
                        status_code=f"Error: {str(e)}",
                        timestamp=get_timestamp()
                    )
                    print(f"{api['name']} - Error: {str(e)}, Time: {get_timestamp()}")

                # Random interval between 0 and 3 minutes (0 to 180 seconds)
                random_interval = random.randint(0, 180)
                time.sleep(random_interval)

# Endpoint to retrieve logs with pagination
@app.route("/logs", methods=["GET"])
def get_logs():
    """Retrieve the last 20 API logs."""
    return jsonify(list(api_logs))  # Return logs directly as a list

# Endpoint to check server status and log the call
@app.route("/keep-alive", methods=["GET"])
def keep_alive():
    """Check if the server is running."""
    timestamp = get_timestamp()
    log_api_response(name="Keep Alive", status_code=200, timestamp=timestamp)
    return jsonify({"message": "The server is alive and running!", "timestamp": timestamp})

# Main logic
if __name__ == "__main__":
    # Start thread to ping APIs without overlapping
    threading.Thread(target=ping_apis_without_overlap, daemon=True).start()

    # Run Flask app
    app.run(host="0.0.0.0", port=5001)
