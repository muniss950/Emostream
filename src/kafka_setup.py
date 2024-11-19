from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import time

# Kafka configuration
bootstrap_servers = 'localhost:9092'
topics = ['emoji_stream', 'processed_emojis']  # List of general topics to check
cluster_count = 4  # Cluster range from 0 to 3 (4 clusters)
subscribers_per_cluster = 3  # Number of subscribers per cluster (for example 3 subscribers)

def check_and_create_topics_and_subscribers():
    # Initialize the Kafka Admin client
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        client_id='kafka_topic_creator'
    )
    
    # Get the list of existing topics
    existing_topics = admin_client.list_topics()
    print(f"Existing topics: {existing_topics}")

    # Create general topics if they don't exist
    for topic in topics:
        if topic not in existing_topics:
            print(f"Creating topic: {topic}")
            new_topic = NewTopic(name=topic, num_partitions=3, replication_factor=1)
            try:
                # Create the topic
                admin_client.create_topics(new_topics=[new_topic], validate_only=False)
                print(f"Topic {topic} created successfully.")
            except TopicAlreadyExistsError:
                print(f"Topic {topic} already exists.")
        else:
            print(f"Topic {topic} already exists.")
    
    # Create cluster-specific topics
    for i in range(cluster_count):
        cluster_topic = f"cluster_{i}_topic"
        if cluster_topic not in existing_topics:
            print(f"Creating cluster topic: {cluster_topic}")
            new_topic = NewTopic(name=cluster_topic, num_partitions=3, replication_factor=1)
            try:
                admin_client.create_topics(new_topics=[new_topic], validate_only=False)
                print(f"Cluster topic {cluster_topic} created successfully.")
            except TopicAlreadyExistsError:
                print(f"Cluster topic {cluster_topic} already exists.")
        else:
            print(f"Cluster topic {cluster_topic} already exists.")
        
        # Create subscriber topics for each cluster (e.g., subscriber_0_0, subscriber_1_0, etc.)
        for subscriber_id in range(subscribers_per_cluster):
            subscriber_topic = f"subscriber_{i}_{subscriber_id}"
            if subscriber_topic not in existing_topics:
                print(f"Creating subscriber topic: {subscriber_topic}")
                new_topic = NewTopic(name=subscriber_topic, num_partitions=3, replication_factor=1)
                try:
                    admin_client.create_topics(new_topics=[new_topic], validate_only=False)
                    print(f"Subscriber topic {subscriber_topic} created successfully.")
                except TopicAlreadyExistsError:
                    print(f"Subscriber topic {subscriber_topic} already exists.")
            else:
                print(f"Subscriber topic {subscriber_topic} already exists.")
    
    admin_client.close()

def ensure_topics_exist():
    max_retries = 5
    retry_interval = 2
    
    for _ in range(max_retries):
        try:
            check_and_create_topics_and_subscribers()
            return True
        except Exception as e:
            print(f"Error creating topics and subscribers: {str(e)}")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
    
    return False

if __name__ == "__main__":
    ensure_topics_exist()  # Ensure topics and subscribers are created

