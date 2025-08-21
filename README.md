# EmoStream: Real-time Emoji Processing System

![image](https://github.com/user-attachments/assets/1d731357-83e1-443a-b3d6-e5bf6f1cf27c)

What is this? A fun system that lets you send emojis and broadcast them to multiple people in real-time!

Think of it like: A group chat where everyone can send emojis and see them instantly, but built with enterprise-grade technology.

Perfect for: Learning about distributed systems, real-time messaging, or just having fun with emojis!

Overview
EmoStream is a distributed system that enables real-time emoji broadcasting and processing. It uses an event-driven architecture with Kafka as the message broker to handle concurrent emoji submissions and broadcasting to multiple subscribers.

🏗️ What's Happening? (Simple Version)
The Magic: When you send an emoji, it goes through this journey:

📱 You → Send emoji via API
🖥️ Flask App → Receives emoji and sends it to Kafka
📨 Kafka → Stores and distributes the emoji to all subscribers
📡 Subscribers → Receive emoji and can send it to connected clients
👥 Everyone → Gets the emoji in real-time!
Why Kafka? It's like a super-fast post office that never loses letters and can handle millions of messages per second!

Why Multiple Subscribers? So many people can connect at once without slowing down the system.

Features
Real-time emoji broadcasting
Concurrent client support
Event-driven architecture
Scalable subscriber system
RESTful API for client management
Health monitoring and logging
Docker containerization
Prerequisites
Docker
Docker Compose
Python 3.9+
Kafka (provided via Docker)
🚀 Quick Start (For Anyone!)
Choose your adventure:

⚡ Super Quick (3 commands)
See QUICKSTART.md for the fastest way to get running!

📖 Step-by-Step
See INSTALL.md for detailed installation instructions.

🎯 Right Here (Summary)
# 1. Get the code (download ZIP or git clone)
# 2. Start everything
docker-compose up --build -d

# 3. Test it works
curl http://localhost:5000/

# 4. Send your first emoji
curl -X POST http://localhost:5000/emoji \
  -H "Content-Type: application/json" \
  -d '{"emoji_type": "😊", "timestamp": "2025-08-13T20:45:00Z"}'
🎉 That's it! Your EmoStream is now running!

🎯 Try It Out!
Test the API with Simple Commands
1. Send an Emoji
curl -X POST http://localhost:5000/emoji \
  -H "Content-Type: application/json" \
  -d '{"emoji_type": "😊", "timestamp": "2025-08-13T20:45:00Z"}'
Expected response:

{
  "message": "Emoji sent successfully"
}
2. Register a Client
curl -X POST http://localhost:5000/register_client \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my_first_client"}'
Expected response:

{
  "message": "Client my_first_client successfully registered.",
  "assigned_subscriber": {
    "cluster_id": 1,
    "subscriber_id": 2,
    "port": 6005
  }
}
3. List All Clients
curl http://localhost:5000/list_clients
Expected response:

{
  "my_first_client": {
    "cluster_id": 1,
    "subscriber_id": 2,
    "port": 6005
  }
}
4. Deregister a Client
curl -X POST http://localhost:5000/deregister_client \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my_first_client"}'
Expected response:

{
  "message": "Client my_first_client deregistered successfully"
}
🎮 Interactive Testing
Want to test without command line? Use these tools:

Postman - Import the requests above
Insomnia - Copy the curl commands
Browser - For GET requests like http://localhost:5000/
📱 Test with Different Emojis
Try these emoji types:

😊 (smile)
😂 (laugh)
❤️ (heart)
👍 (thumbs up)
🎉 (party)
🚀 (rocket)
🌟 (star)
🧪 Testing
🚀 Quick Demo (Recommended for first-time users)
# Linux/Mac
./demo.sh

# Windows
demo.bat
What the demo does:

✅ Tests health endpoint
✅ Sends a test emoji
✅ Registers a test client
✅ Lists all clients
✅ Shows you everything is working!
🔬 Run the Built-in Tests
# Run all tests
docker-compose up test

# Or use the Makefile
make test
What the tests do:

✅ Test client registration
✅ Test emoji submission
✅ Test client deregistration
✅ Simulate 100+ concurrent users
✅ Test message delivery performance
🚨 Troubleshooting
"Docker not found" Error
# Install Docker first:
# Windows/Mac: Download from https://docker.com
# Linux: sudo apt install docker.io docker-compose
"Port already in use" Error
# Stop any existing services
docker-compose down

# Or kill processes using ports 5000, 9092, 2181
"Connection refused" Error
# Wait longer for services to start
# Check status:
docker-compose ps

# View logs:
docker-compose logs app
"Permission denied" Error (Linux)
# Add your user to docker group
sudo usermod -aG docker $USER
# Then logout and login again
📊 Check System Status
# See all running services
docker-compose ps

# View real-time logs
docker-compose logs -f

# Check specific service logs
docker-compose logs app
docker-compose logs kafka
🛑 Stop Everything
# Stop all services
docker-compose down

# Or use the Makefile
make down

# Remove everything (including data)
docker-compose down -v
⚙️ Configuration
For most people: You don't need to change anything! The defaults work perfectly.

For developers: You can customize these settings:

KAFKA_BROKER: Kafka broker address (default: kafka:29092)
FLASK_APP: Flask application entry point (default: src/app.py)
FLASK_ENV: Environment (default: development)
Monitoring
Container health checks
Logging to /app/logs
Kafka topic monitoring
Client connection tracking
🎯 Common Commands (Copy & Paste)
# Start everything
docker-compose up --build -d

# Check if it's working
curl http://localhost:5000/

# Send an emoji
curl -X POST http://localhost:5000/emoji \
  -H "Content-Type: application/json" \
  -d '{"emoji_type": "😊", "timestamp": "2025-08-13T20:45:00Z"}'

# Stop everything
docker-compose down

# View logs
docker-compose logs -f
🤝 Contributing
Fork the repository
Create a feature branch
Commit your changes
Push to the branch
Create a Pull Request
Need help? Open an issue or check the troubleshooting section above!

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Kafka for message queuing
Flask for the web framework
Docker for containerization
