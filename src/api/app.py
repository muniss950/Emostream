from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

# Initialize the Kafka producer to send emojis to 'processed_emojis' topic
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

@app.route('/emoji', methods=['POST'])
def send_emoji():
    try:
        # Get emoji data from the request body
        data = request.get_json()
        print(data)
        emoji = data.get("emoji", "")
        
        if not emoji:
            return jsonify({"error": "No emoji provided"}), 400

        # Publish emoji to the 'processed_emojis' Kafka topic
        producer.send('processed_emojis', value={"timestamp":data.get("timestamp",""),"emoji": emoji})
        
        return jsonify({"message": "Emoji sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

