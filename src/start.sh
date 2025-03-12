
#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Create empty log files
touch logs/app.log logs/publisher.log logs/consumer.log logs/subscriber.log logs/register.log

# Start the main application
echo "Starting app.py..."
python3 app.py > logs/app.log 2>&1 &

# Start the Kafka publisher
echo "Starting publisher.py..."
python3 publisher.py > logs/publisher.log 2>&1 &

# Start the Kafka consumer
echo "Starting consumer.py..."
python3 consumer.py > logs/consumer.log 2>&1 &

# Start the subscriber
echo "Starting subscriber.py..."
python3 subscriber.py > logs/subscriber.log 2>&1 &

# Start the register service
echo "Starting register.py..."
python3 register.py > logs/register.log 2>&1 &

echo "All services started."

# Wait for all processes
wait
