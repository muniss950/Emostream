from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Example mapping of subscriber topic -> port
# For simplicity, there are 3 clusters, and each cluster has 3 subscribers.
SUBSCRIBER_PORTS = {
    0: [5001, 5002, 5003],  # Cluster 0, Subscribers 0, 1, 2
    1: [5004, 5005, 5006],  # Cluster 1, Subscribers 0, 1, 2
    2: [5007, 5008, 5009]   # Cluster 2, Subscribers 0, 1, 2
}

# A dictionary to store client -> port mapping
client_port_mapping = {}

@app.route('/register', methods=['POST'])
def register_client():
    """
    Register the client and assign them a unique port for the subscriber.
    This will send the port information back to the client.
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Randomly select a cluster (0-2)
        cluster_id = random.choice([0, 1, 2])
        
        # Randomly select a subscriber from the selected cluster
        subscriber_id = random.choice([0, 1, 2])
        
        # Get the port for the selected subscriber in the cluster
        port = SUBSCRIBER_PORTS[cluster_id][subscriber_id]
        
        # Store the client -> port mapping
        client_port_mapping[user_id] = {
            "cluster_id": cluster_id,
            "subscriber_id": subscriber_id,
            "port": port
        }

        # Return the assigned port to the client
        return jsonify({
            "message": f"Client {user_id} registered successfully.",
            "assigned_port": port
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clients', methods=['GET'])
def list_clients():
    """
    List all registered clients and their assigned ports.
    """
    return jsonify(client_port_mapping), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
