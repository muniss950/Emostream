# EmoStream: Real-time Emoji Processing System

A scalable system for processing and broadcasting emoji reactions in real-time using Apache Kafka and PySpark.

## Architecture

- **API Layer**: Flask server receiving emoji reactions
- **Message Queue**: Apache Kafka for reliable message streaming
- **Processing Engine**: PySpark for real-time data processing
- **Distribution Layer**: Publisher-Subscriber model for scalable message delivery

## Components

1. **API Server** (`src/api/app.py`)
   - Receives emoji reactions
   - Batches and sends to Kafka

2. **Stream Processor** (`src/streaming/consumer.py`)
   - Processes emoji data in 2-second windows
   - Applies 1000:1 scaling rule
   - Outputs processed data to Kafka

3. **Publisher-Subscriber System** (`src/pubsub/`)
   - Main publisher distributes to clusters
   - Cluster publishers manage subscriber groups
   - Subscribers deliver to end clients

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start Kafka and Zookeeper:
   ```bash
   # Using Docker or your preferred method
   ```

3. Run components:
   ```bash
   # Start API server
   npm start

   # Start stream processor
   npm run consumer
   ```

## Testing

Run tests:
```bash
npm test
```

## Features

- Handles 1000s of concurrent emoji reactions
- Processes data in 2-second windows
- Scales horizontally with multiple clusters
- Real-time data delivery to clients