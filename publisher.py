from kafka import KafkaConsumer, KafkaProducer
import json
import threading

class MainPublisher:
    def __init__(self, clusters=3):
        self.consumer = KafkaConsumer(
            'processed_emojis',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.producers = []
        for i in range(clusters):
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            self.producers.append(producer)

    def start(self):
        try:
            for message in self.consumer:
                # print(message.value)
                # Distribute to all clusters
                for i, producer in enumerate(self.producers):
                    producer.send(f'cluster_{i}_topic', value=message.value)
        except Exception as e:
            print(f"Error in main publisher: {str(e)}")

class ClusterPublisher:
    def __init__(self, cluster_id):
        self.cluster_id = cluster_id
        self.consumer = KafkaConsumer(
            f'cluster_{cluster_id}_topic',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.subscribers = set()
        self.lock = threading.Lock()

    def add_subscriber(self, subscriber_id):
        
        with self.lock:
            self.subscribers.add(subscriber_id)

    def remove_subscriber(self, subscriber_id):
        with self.lock:
            self.subscribers.remove(subscriber_id)

    def start(self):
        try:
            for message in self.consumer:
                with self.lock:
                    # Broadcast to all subscribers
                    print(message.value)
                    print(self.subscribers)
                    for subscriber_id in self.subscribers:
                        # Send to subscriber-specific topic
                        producer = KafkaProducer(
                            bootstrap_servers=['localhost:9092'],
                            value_serializer=lambda x: json.dumps(x).encode('utf-8')
                        )
                        print(f"sent to subscriber_{self.cluster_id}_{subscriber_id}")
                        producer.send(f'subscriber_{self.cluster_id}_{subscriber_id}', value=message.value)
        except Exception as e:
            print(f"Error in cluster {self.cluster_id}: {str(e)}")

def main():
    # Start main publisher
    main_publisher = MainPublisher(clusters=3)
    main_thread = threading.Thread(target=main_publisher.start)
    main_thread.start()

    # Start cluster publishers
    cluster_publishers = []
    cluster_threads = []
    for i in range(4):
        publisher = ClusterPublisher(i)
        cluster_publishers.append(publisher)
        publisher.add_subscriber(0)
        publisher.add_subscriber(1)
        publisher.add_subscriber(2)
        thread = threading.Thread(target=publisher.start)
        cluster_threads.append(thread)
        thread.start()

    # Wait for all threads
    main_thread.join()
    for thread in cluster_threads:
        thread.join()

if __name__ == "__main__":
    main()
