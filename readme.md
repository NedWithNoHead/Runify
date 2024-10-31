# Runify - Event Processing System

## Project Overview
A microservices-based system that processes and analyzes running and music data. The system uses a combination of REST APIs, message queues, and databases to handle event processing in a distributed manner.

## Architecture
The system consists of three main services:
- Receiver Service
- Storage Service
- Analyzer Service

And three infrastructure components:
- Kafka Message Broker
- Zookeeper
- MySQL Database

## Services

### 1. Receiver Service
- Entry point for new events
- **Endpoints**:
  - `POST /stats/running` - Submit running statistics
  - `POST /stats/music` - Submit music information
- **Features**:
  - Validates incoming requests
  - Generates trace IDs
  - Produces messages to Kafka

### 2. Storage Service
- Purpose: Permanent data storage
- **Endpoints**:
  - `GET /stats/running` - Retrieve running events by date range
  - `GET /stats/music` - Retrieve music events by date range
- **Features**:
  - Consumes Kafka messages
  - Stores data in MySQL
  - Provides date-based querying

### 3. Analyzer Service
- Purpose: Event analysis and statistics
- **Endpoints**:
  - `GET /running?index={n}` - Get specific running event by index
  - `GET /music?index={n}` - Get specific music event by index
  - `GET /stats` - Get event statistics
- **Features**:
  - Reads Kafka message history
  - Provides event counts
  - Index-based event retrieval

## Setup Instructions

### Prerequisites
- Python 3.x
- Docker and Docker Compose
- Azure VM or similar cloud instance
- PostMan for testing

### Environment Setup
1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv runify_venv
source runify_venv/bin/activate  # Linux/Mac
runify_venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with required configuration
# See .env.example for required variables
```

### Infrastructure Setup
1. Start infrastructure services:
```bash
docker compose up -d
```

2. Verify services are running:
```bash
docker ps
```

### Starting Services
Start services in this order:
1. Storage Service
2. Receiver Service
3. Analyzer Service

From each service directory:
```bash
python app.py
```

## Testing

### Sample Requests

1. Submit Running Data:
```bash
POST /stats/running
{
    "user_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "duration": 3600,
    "distance": 5000,
    "timestamp": "2024-09-10T09:12:33.001Z"
}
```

2. Submit Music Data:
```bash
POST /stats/music
{
    "user_id": "d999f1ee-6c54-4b01-90e6-d701748f0851",
    "song_name": "Run Boy Run",
    "artist": "Woodkid",
    "song_duration": 180,
    "timestamp": "2024-09-10T09:12:33.001Z"
}
```

3. Query Events:
```bash
# Get running events by date range
GET /stats/running?start_timestamp=2024-01-01T00:00:00Z&end_timestamp=2024-12-31T23:59:59Z

# Get first running event from history
GET /running?index=0

# Get event statistics
GET /stats
```

## Security Notes
- Port numbers and connection details should be stored in environment variables
- Never commit .env files to version control
- Use secure passwords and update them regularly
- Restrict access to your infrastructure components
- Keep all packages and dependencies up to date

## Troubleshooting

### Common Issues

1. Connection Issues:
- Check if all services are running
- Verify environment variables are set correctly
- Ensure all required ports are accessible

2. Message Processing Issues:
- Check Kafka consumer logs
- Verify message format matches expected schema
- Ensure database connection is active
