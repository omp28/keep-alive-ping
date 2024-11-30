import random
import time
from datetime import datetime
from flask import Flask, jsonify, request
import requests
import os
import threading
from collections import deque

# Flask app for hosting the API
app = Flask(__name__)

# In-memory log storage using deque for thread-safe, fixed-size logs
api_logs = deque(maxlen=20)  # Keep the last 1000 logs

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
        "name": "Self Ping API",
        "url": "https://keep-alive-khaki.vercel.app/ping",
        "method": "GET"
    }
]

MARKETPLACE_URLS = [
    {"name": "Marketplace Men API", "url": "https://marketplace.omp28.me/_next/data/A69ycs2melZjH8welEB84/men.json"},
    {"name": "Marketplace Women API", "url": "https://marketplace.omp28.me/_next/data/A69ycs2melZjH8welEB84/women.json"}
]

QUICKCHAT_API = {
    "name": "QuickChat Login API",
    "url": "https://quickchat-m4ji.onrender.com/api/user/login",
    "method": "POST",
    "data": {
        "email": "dummy@example.com",  # Replace with actual email
        "password": "password123"      # Replace with actual password
    }
}


# Helper function to get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to log API responses (excluding response body)
def log_api_response(name, status_code, timestamp):
    log_entry = {
        "name": name,
        "timestamp": timestamp,
        "status_code": status_code
    }
    api_logs.appendleft(log_entry)

# Graceful shutdown mechanism
shutdown_event = threading.Event()

# Function to ping APIs at random intervals
def ping_apis():
    while not shutdown_event.is_set():
        for api in APIS:
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
                    name=api['name'],
                    status_code="Timeout",
                    timestamp=get_timestamp()
                )
                print(f"{api['name']} - Timeout Error, Time: {get_timestamp()}")
            except requests.exceptions.RequestException as e:
                log_api_response(
                    name=api['name'],
                    status_code=f"Error: {str(e)}",
                    timestamp=get_timestamp()
                )
                print(f"{api['name']} - Error: {str(e)}, Time: {get_timestamp()}")

            random_interval = random.randint(30, 180)  # 30 to 180 seconds
            time.sleep(random_interval)

# Function to ping Marketplace APIs alternately at random intervals
def ping_marketplace():
    index = 0
    while not shutdown_event.is_set():
        try:
            url = MARKETPLACE_URLS[index]["url"]
            name = MARKETPLACE_URLS[index]["name"]
            response = requests.get(url)

            log_api_response(
                name=name,
                status_code=response.status_code,
                timestamp=get_timestamp()
            )
            print(f"{name} - Status: {response.status_code}, Time: {get_timestamp()}")
        except requests.exceptions.Timeout:
            log_api_response(
                name=name,
                status_code="Timeout",
                timestamp=get_timestamp()
            )
            print(f"{name} - Timeout Error, Time: {get_timestamp()}")
        except requests.exceptions.RequestException as e:
            log_api_response(
                name=name,
                status_code=f"Error: {str(e)}",
                timestamp=get_timestamp()
            )
            print(f"{name} - Error: {str(e)}, Time: {get_timestamp()}")

        index = 1 - index  # Alternate between 0 and 1
        random_interval = random.randint(30, 180)  # 30 to 180 seconds
        time.sleep(random_interval)

# Function to ping self-hosted API at random intervals
def ping_self():
    while not shutdown_event.is_set():
        try:
            response = requests.get("https://keep-alive-khaki.vercel.app/ping")
            log_api_response(
                name="Self Ping API",
                status_code=response.status_code,
                timestamp=get_timestamp()
            )
            print(f"Self Ping API - Status: {response.status_code}, Time: {get_timestamp()}")
        except requests.exceptions.Timeout:
            log_api_response(
                name="Self Ping API",
                status_code="Timeout",
                timestamp=get_timestamp()
            )
            print(f"Self Ping API - Timeout Error, Time: {get_timestamp()}")
        except requests.exceptions.RequestException as e:
            log_api_response(
                name="Self Ping API",
                status_code=f"Error: {str(e)}",
                timestamp=get_timestamp()
            )
            print(f"Self Ping API - Error: {str(e)}, Time: {get_timestamp()}")

        random_interval = random.randint(30, 180)  # 30 to 180 seconds
        time.sleep(random_interval)

# Function to ping QuickChat API with random intervals
def ping_quickchat():
    while not shutdown_event.is_set():
        try:
            response = requests.post(QUICKCHAT_API["url"], json=QUICKCHAT_API["data"])
            log_api_response(
                name=QUICKCHAT_API["name"],
                status_code=response.status_code,
                timestamp=get_timestamp()
            )
            print(f"{QUICKCHAT_API['name']} - Status: {response.status_code}, Time: {get_timestamp()}")
        except requests.exceptions.Timeout:
            log_api_response(
                name=QUICKCHAT_API["name"],
                status_code="Timeout",
                timestamp=get_timestamp()
            )
            print(f"{QUICKCHAT_API['name']} - Timeout Error, Time: {get_timestamp()}")
        except requests.exceptions.RequestException as e:
            log_api_response(
                name=QUICKCHAT_API["name"],
                status_code=f"Error: {str(e)}",
                timestamp=get_timestamp()
            )
            print(f"{QUICKCHAT_API['name']} - Error: {str(e)}, Time: {get_timestamp()}")

        random_interval = random.randint(30, 180)  # 30 to 180 seconds
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
    # Threads for different APIs
    threading.Thread(target=ping_apis, daemon=True).start()           # General APIs
    threading.Thread(target=ping_marketplace, daemon=True).start()    # Marketplace APIs
    threading.Thread(target=ping_self, daemon=True).start()           # Self Ping
    threading.Thread(target=ping_quickchat, daemon=True).start()      # QuickChat API

    # Run Flask app
    app.run(host="0.0.0.0", port=5000)
