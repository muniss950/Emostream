import argparse
import requests

# Base URL of the Flask API
API_BASE_URL = "http://localhost:5000"

def register_client(client_id):
    url = f"{API_BASE_URL}/register_client"
    data = {"client_id": client_id}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"Successfully registered client {client_id}.")
        print("Assigned subscriber:", response.json())
    else:
        print(f"Failed to register client {client_id}.")
        print("Error:", response.json())

def deregister_client(client_id):
    url = f"{API_BASE_URL}/deregister_client"
    data = {"client_id": client_id}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"Successfully deregistered client {client_id}.")
    else:
        print(f"Failed to deregister client {client_id}.")
        print("Error:", response.json())

def list_clients():
    url = f"{API_BASE_URL}/list_clients"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Registered clients:")
        clients = response.json()
        if clients:
            for client_id, subscriber in clients.items():
                print(f"  Client ID: {client_id}, Subscriber: {subscriber}")
        else:
            print("  No clients registered.")
    else:
        print("Failed to retrieve client list.")
        print("Error:", response.json())

def main():
    parser = argparse.ArgumentParser(description="Client Registration CLI Tool")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Commands")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a client")
    register_parser.add_argument("client_id", type=str, help="Client ID to register")
    
    # Deregister command
    deregister_parser = subparsers.add_parser("deregister", help="Deregister a client")
    deregister_parser.add_argument("client_id", type=str, help="Client ID to deregister")
    
    # List clients command
    list_parser = subparsers.add_parser("list", help="List all registered clients")
    
    args = parser.parse_args()
    
    if args.command == "register":
        register_client(args.client_id)
    elif args.command == "deregister":
        deregister_client(args.client_id)
    elif args.command == "list":
        list_clients()

if __name__ == "__main__":
    main()
