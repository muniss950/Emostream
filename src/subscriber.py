# import json
# import threading
# from kafka import KafkaConsumer
# import socket
#
# class Subscriber:
#     def __init__(self, cluster_id, subscriber_id, port):
#         self.cluster_id = cluster_id
#         self.subscriber_id = subscriber_id
#         self.port = port
#         self.topic = f'subscriber_{cluster_id}_{subscriber_id}'
#         self.consumer = KafkaConsumer(
#             self.topic,
#             bootstrap_servers=['localhost:9092'],
#             value_deserializer=lambda x: json.loads(x.decode('utf-8'))
#         )
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_socket.bind(('0.0.0.0', self.port))
#         self.server_socket.listen(1)  # Only one client connection allowed
#         self.active = True
#         self.client_socket = None
#
#     def start(self):
#         print(f"Subscriber {self.cluster_id}_{self.subscriber_id} listening on port {self.port}")
#         threading.Thread(target=self.accept_client, daemon=True).start()
#         self.listen_to_topic()
#
#     def accept_client(self):
#         """Accept a single client connection."""
#         while self.active:
#             try:
#                 self.client_socket, address = self.server_socket.accept()
#                 print(f"Client connected at {address}")
#             except Exception as e:
#                 print(f"Error accepting client: {str(e)}")
#                 break
#
#     def listen_to_topic(self):
#         """Listen to Kafka topic and forward messages to the connected client."""
#         try:
#             while self.active:
#                 if not self.client_socket:  # Wait for client connection
#                     continue
#
#                 messages = self.consumer.poll(timeout_ms=1000)
#                 for topic_partition, records in messages.items():
#                     for record in records:
#                         self.process_message(record.value)
#                         self.send_message_to_client(record.value)
#         except Exception as e:
#             print(f"Error in subscriber {self.subscriber_id}: {str(e)}")
#
#     def send_message_to_client(self, message):
#         """Send the processed message to the connected client."""
#         try:
#             if self.client_socket:
#                 self.client_socket.sendall(json.dumps(message).encode('utf-8'))
#                 print(f"Message sent to client by {self.cluster_id}_{self.subscriber_id}")
#             else:
#                 print("No client connected, unable to send message")
#         except Exception as e:
#             print(f"Error sending message to client: {str(e)}")
#             self.client_socket = None  # Reset client socket on error
#
#     def process_message(self, message):
#         """Process and log received Kafka messages."""
#         print(f"Subscriber {self.cluster_id}_{self.subscriber_id} received: {message}")
#
#     def stop(self):
#         """Stop the subscriber and close resources."""
#         self.active = False
#         if self.client_socket:
#             self.client_socket.close()
#         self.server_socket.close()
#         self.consumer.close()
#
#
# # Create a dictionary for cluster and subscriber mapping
# subscriber_mapping = {
#     "0_0": 6000, "0_1": 6001, "0_2": 6002,
#     "1_0": 6003, "1_1": 6004, "1_2": 6005,
#     "2_0": 6006, "2_1": 6007, "2_2": 6008
# }
#
#
# def main():
#     # Create subscribers
#     subscribers = []
#     threads = []
#
#     # Assume there are 3 clusters (0-2) and each cluster has 3 subscribers
#     for cluster_id in range(3):  # Cluster range 0 to 2
#         for subscriber_id in range(3):  # Create 3 subscribers per cluster
#             key = f"{cluster_id}_{subscriber_id}"
#             port = subscriber_mapping[key]
#             subscriber = Subscriber(cluster_id, subscriber_id, port)
#             subscribers.append(subscriber)
#             thread = threading.Thread(target=subscriber.start)
#             threads.append(thread)
#             thread.start()
#
#     try:
#         while True:  # Keep the subscribers running
#             pass
#     except KeyboardInterrupt:
#         print("Shutting down subscribers...")
#         for subscriber in subscribers:
#             subscriber.stop()
#
#
# if __name__ == "__main__":
#     main()
#
import json
import asyncio
import websockets
from kafka import KafkaConsumer

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
        self.active = True
        self.connected_clients = set()  # Track WebSocket clients

    async def websocket_handler(self, websocket):
        """Handles WebSocket connections."""
        self.connected_clients.add(websocket)
        print(f"Client connected to {self.cluster_id}_{self.subscriber_id}")

        try:
            while self.active:
                await asyncio.sleep(1)  # Keep connection alive
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected from {self.cluster_id}_{self.subscriber_id}")
        finally:
            self.connected_clients.remove(websocket)

    async def listen_to_topic(self):
        """Listen to Kafka topic and forward messages to WebSocket clients."""
        while self.active:
            messages = self.consumer.poll(timeout_ms=1000)
            for _, records in messages.items():
                for record in records:
                    message = record.value
                    # print(f"Subscriber {self.cluster_id}_{self.subscriber_id} received: {message}")
                    await self.broadcast_message(message)
            await asyncio.sleep(1)

    async def broadcast_message(self, message):
        """Send the Kafka message to all connected WebSocket clients."""
        if self.connected_clients:
            message_str = json.dumps(message)
            await asyncio.gather(*[client.send(message_str) for client in self.connected_clients])

    async def start(self):
        """Start WebSocket server and Kafka listener."""
        server = await websockets.serve(self.websocket_handler, "localhost", self.port)
        print(f"Subscriber {self.cluster_id}_{self.subscriber_id} WebSocket running on port {self.port}")

        await asyncio.gather(self.listen_to_topic(), server.wait_closed())

    def stop(self):
        """Stop the subscriber."""
        self.active = False
        self.consumer.close()

# Cluster & subscriber mapping
subscriber_mapping = {
    "0_0": 6000, "0_1": 6001, "0_2": 6002,
    "1_0": 6003, "1_1": 6004, "1_2": 6005,
    "2_0": 6006, "2_1": 6007, "2_2": 6008
}

async def main():
    """Create and start all subscribers asynchronously."""
    subscribers = []
    tasks = []

    for cluster_id in range(3):
        for subscriber_id in range(3):
            key = f"{cluster_id}_{subscriber_id}"
            port = subscriber_mapping[key]
            subscriber = Subscriber(cluster_id, subscriber_id, port)
            subscribers.append(subscriber)
            tasks.append(subscriber.start())

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down subscribers...")
