import requests
import socket
import json
import random
from datetime import datetime
import threading
import time
import argparse

API_URL = "http://localhost:5000/register_client"
EMOJI_SEND_DELAY = 0.1    # Delay between emoji sends in seconds
BURST_DELAY = 0.5         # Delay between bursts in seconds
NUM_THREADS = 5          # Number of concurrent users

stop_threads = threading.Event()  # Event to signal threads to stop


def send_emoji(thread_id):
    """Function to send emoji data to the server."""
    emojis = ["😊", "😂", "❤️", "👍", "🎉"]
    count = 0

    while not stop_threads.is_set():
        # Send a burst of emojis
        for _ in range(500):  # Adjust burst size for performance tuning
            if stop_threads.is_set():
                break

            data = {
                "user_id": f"user_{thread_id}_{random.randint(1, 1000)}",
                "emoji_type": random.choice(emojis),
                "timestamp": datetime.now().isoformat()
            }

            try:
                response = requests.post('http://localhost:5000/emoji', json=data)
                if response.status_code == 200:
                    count += 1
                    if count % 100 == 0:  # Log every 100 emojis
                        print(f"Thread {thread_id}: Sent {count} emojis")
                else:
                    print(f"Thread {thread_id}: Error {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Thread {thread_id}: Error - {str(e)}")

            time.sleep(EMOJI_SEND_DELAY)  # Small delay between emojis in burst

        time.sleep(BURST_DELAY)  # Delay between bursts


def register_with_server(client_id):
    """Register the client with the server and get assigned subscriber details."""
    try:
        response = requests.post(API_URL, json={"client_id": client_id})
        response.raise_for_status()
        subscriber_info = response.json()
        print(f"Assigned to subscriber: {subscriber_info}")
        return subscriber_info
    except requests.RequestException as e:
        print(f"Error registering with server: {str(e)}")
        return None


def connect_to_subscriber(host, port):
    """Connect to the assigned subscriber and listen for messages."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to subscriber at {host}:{port}")

        while not stop_threads.is_set():
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            message = json.loads(data)
            print(f"Received message from subscriber: {message}")
    except Exception as e:
        print(f"Error connecting to subscriber: {str(e)}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emoji Sender Client")
    parser.add_argument(
        "--client-id", type=str, required=True,
        help="Unique identifier for the client"
    )
    args = parser.parse_args()
    client_id = args.client_id

    subscriber_info = register_with_server(client_id)
    if subscriber_info:
        threading.Thread(
            target=connect_to_subscriber,
            args=('localhost', subscriber_info["assigned_subscriber"]["port"]),
            daemon=True
        ).start()

    threads = []
    print("Starting emoji senders (Press Ctrl+C to stop)")

    try:
        # Create and start threads
        for i in range(NUM_THREADS):
            thread = threading.Thread(target=send_emoji, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            print(f"Started sender thread {i}")

        # Keep the main thread alive
        while not stop_threads.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping emoji senders...")
        stop_threads.set()  # Signal all threads to stop

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    print("All threads stopped.")
