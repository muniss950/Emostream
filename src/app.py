from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import threading
import time

app = Flask(__name__)

# Initialize the Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# A flag to manage the flushing thread
flushing = True

def flush_kafka_producer(interval=0.5):
    """Flush Kafka producer at regular intervals."""
    while flushing:
        time.sleep(interval)
        producer.flush()

# Start a thread to periodically flush the Kafka producer
flush_thread = threading.Thread(target=flush_kafka_producer, args=(0.5,), daemon=True)
flush_thread.start()

@app.route('/emoji', methods=['POST'])
def send_emoji():
    try:
        # Get emoji data from the request body
        data = request.get_json()
        print(data)
        emoji = data.get("emoji_type", "")
        
        if not emoji:
            return jsonify({"error": "No emoji provided"}), 400

        # Publish emoji to the 'emoji_stream' Kafka topic
        producer.send('emoji_stream', value={
            "timestamp": data.get("timestamp", ""),
            "emoji_type": emoji
        })
        
        return jsonify({"message": "Emoji sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Endpoint to safely shut down the app."""
    global flushing
    flushing = False
    flush_thread.join()
    producer.close()
    return jsonify({"message": "Producer and app shut down successfully"}), 200

if __name__ == "__main__":
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        flushing = False
        flush_thread.join()
        producer.close()

