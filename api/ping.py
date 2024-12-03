import requests
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# URLs and payloads for different tasks
TASKS = [
    {
        "name": "Keep QuickChat Login Alive",
        "url": "https://quickchat-m4ji.onrender.com/api/user/login",
        "method": "POST",
        "data": {"email": "dummy@example.com", "password": "password123"},
        "interval": 150  # Interval in seconds (2.5 minutes)
    },
    {
        "name": "Keep Vectorshift Server Awake",
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
        },
        "interval": 180  # Interval in seconds (3 minutes)
    },
    {
        "name": "Keep Marketplace Server Awake",
        "url": "https://marketplace.omp28.me/_next/data/A69ycs2melZjH8welEB84/men.json",
        "method": "GET",
        "data": None,  # No payload for GET request
        "interval": 160  # Interval in seconds (2.67 minutes)
    }
]

def ping_task(task):
    """Function to continuously ping a task based on its configuration."""
    while True:
        start_time = time.time()  # Track response time
        try:
            logging.info(f"[{task['name']}] Sending {task['method']} request to {task['url']}...")

            if task["method"] == "POST":
                response = requests.post(task["url"], json=task["data"], timeout=10)
            else:
                response = requests.get(task["url"], timeout=10)

            # Calculate the time it took to get the response
            elapsed_time = time.time() - start_time
            logging.info(f"[{task['name']}] Response Time: {elapsed_time:.2f} seconds")

            if response.status_code == 200:
                logging.info(f"[{task['name']}] Success! Status code: {response.status_code}")
                if task["method"] == "GET":
                    logging.info(f"[{task['name']}] Response Content (first 200 chars): {response.text[:200]}...")
                else:
                    logging.info(f"[{task['name']}] Response JSON: {response.json()}")
            else:
                logging.warning(f"[{task['name']}] Failed! Status code: {response.status_code}, Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            logging.error(f"[{task['name']}] Timeout error occurred.")
        except requests.exceptions.RequestException as e:
            logging.error(f"[{task['name']}] General error occurred: {e}")
        
        # Wait for the next interval
        time.sleep(task["interval"])

def main():
    """Main function to start all tasks as daemon threads."""
    threads = []
    for task in TASKS:
        thread = threading.Thread(target=ping_task, args=(task,), daemon=True)
        threads.append(thread)
        thread.start()

    # Keep the main thread running to allow daemon threads to operate
    logging.info("All tasks are running in daemon mode. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nExiting...")

if __name__ == "__main__":
    main()
