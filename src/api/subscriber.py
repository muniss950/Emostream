import json
import threading
from kafka import KafkaConsumer, KafkaProducer
import socket
import random

class Subscriber:
    def __init__(self, cluster_id, subscriber_id, port):
        self.cluster_id = cluster_id
        self.subscriber_id = subscriber_id
        self.port = port
        self.topic = f'subscriber_{cluster_id}_{subscriber_id}'
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.active = True

    def start(self):
        print(f"Subscriber {self.cluster_id}_{self.subscriber_id} listening on port {self.port}")
        threading.Thread(target=self.accept_clients, daemon=True).start()
        self.listen_to_topic()

    def accept_clients(self):
        while self.active:
            client_socket, address = self.server_socket.accept()
            print(f"Client connected at {address}")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        try:
            while self.active:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Received from client: {data}")
        finally:
            client_socket.close()

    def listen_to_topic(self):
        try:
            while self.active:
                messages = self.consumer.poll(timeout_ms=1000)
                for topic_partition, records in messages.items():
                    for record in records:
                        self.process_message(record.value)
                        self.send_message(processed_message)
        except Exception as e:
            print(f"Error in subscriber {self.subscriber_id}: {str(e)}")
    def send_message(self, message):
        """
        Send the processed message to the assigned port using a socket.
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', self.port))
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            client_socket.close()
            print(f"Message sent from {self.cluster_id}_{self.subscriber_id} to port {self.port}")
        except Exception as e:
            print(f"Error sending message to port {self.port}: {str(e)}")

    def process_message(self, message):
        print(f"Subscriber {self.cluster_id}_{self.subscriber_id} received: {message}")

    def stop(self):
        self.active = False
        self.server_socket.close()
        self.consumer.close()

# Create a dictionary for cluster and subscriber mapping
subscriber_mapping = {
    "0_0": 6000, "0_1": 6001, "0_2": 6002,
    "1_0": 6003, "1_1": 6004, "1_2": 6005,
    "2_0": 6006, "2_1": 6007, "2_2": 6008
}

def send_message(cluster_id, subscriber_id, message):
    """Send a message to a specific subscriber."""
    key = f"{cluster_id}_{subscriber_id}"
    if key not in subscriber_mapping:
        print(f"No subscriber found for cluster {cluster_id} and subscriber {subscriber_id}")
        return

    port = subscriber_mapping[key]
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', port))
        client_socket.sendall(message.encode('utf-8'))
        print(f"Message sent to subscriber {cluster_id}_{subscriber_id} on port {port}")
        client_socket.close()
    except Exception as e:
        print(f"Error sending message to subscriber {cluster_id}_{subscriber_id}: {str(e)}")

def main():
    # Create subscribers
    subscribers = []
    threads = []

    # Assume there are 3 clusters (0-2) and each cluster has 3 subscribers
    for cluster_id in range(3):  # Cluster range 0 to 2
        for subscriber_id in range(3):  # Create 3 subscribers per cluster
            key = f"{cluster_id}_{subscriber_id}"
            port = subscriber_mapping[key]
            subscriber = Subscriber(cluster_id, subscriber_id, port)
            subscribers.append(subscriber)
            thread = threading.Thread(target=subscriber.start)
            threads.append(thread)
            thread.start()

    # Simulate sending a message to a random subscriber
    try:
        while True:
            cluster_id = random.randint(0, 2)
            subscriber_id = random.randint(0, 2)
            message = json.dumps({"data": "Hello from the publisher"})
            send_message(cluster_id, subscriber_id, message)
    except KeyboardInterrupt:
        print("Shutting down subscribers...")
        for subscriber in subscribers:
            subscriber.stop()

if __name__ == "__main__":
    main()

