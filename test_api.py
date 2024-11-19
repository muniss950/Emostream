import requests
import json
import time
import random
import threading
from datetime import datetime

def send_emoji(thread_id):
    emojis = ["😊", "😂", "❤️", "👍", "🎉"]
    count = 0
    
    while True:
        # Send a burst of emojis
        for _ in range(1000):  # Send 10 emojis in quick succession
            data = {
                "user_id": f"user_{thread_id}_{random.randint(1, 1000)}",
                "emoji_type": random.choice(emojis),
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                response = requests.post('http://localhost:5000/emoji', json=data)
                if response.status_code == 200:
                    count += 1
                    if count % 1000 == 0:  # Log every 100 emojis
                        print(f"Thread {thread_id}: Sent {count} emojis")
                else:
                    print(f"Thread {thread_id}: Error {response.status_code}")
            except Exception as e:
                print(f"Thread {thread_id}: Error - {str(e)}")
            
            time.sleep(0.1)  # Small delay between emojis in burst
        
        time.sleep(0.5)  # Delay between bursts

def main():
    num_threads = 100  # Number of concurrent users
    threads = []
    
    print("Starting emoji senders (Press Ctrl+C to stop)")
    
    try:
        # Create and start threads
        for i in range(num_threads):
            thread = threading.Thread(target=send_emoji, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            print(f"Started sender thread {i}")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping emoji senders...")

if __name__ == "__main__":
    main()
