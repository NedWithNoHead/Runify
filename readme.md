# Runify - Event Processing System

## Architecture Overview
A containerized microservices system that processes running and music data, using:
- REST APIs for synchronous communication
- Kafka for asynchronous messaging
- MySQL for persistent storage
- Docker for containerization

## System Components

### Services
1. **Receiver Service** (Port 8080)
   - Entry point for new events
   - Produces Kafka messages
   - Endpoints:
     - `POST /stats/running` - Submit running statistics
     - `POST /stats/music` - Submit music information

2. **Storage Service** (Port 8090)
   - Manages MySQL database operations
   - Consumes Kafka messages
   - Endpoints:
     - `GET /stats/running` - Retrieve running events by date range
     - `GET /stats/music` - Retrieve music events by date range

3. **Processing Service** (Port 8100)
   - Periodic statistical analysis
   - Endpoints:
     - `GET /stats` - Get aggregated statistics

4. **Analyzer Service** (Port 8110)
   - Kafka message analysis
   - Endpoints:
     - `GET /stats` - Get message queue statistics
     - `GET /running?index=n` - Get specific running event
     - `GET /music?index=n` - Get specific music event

### Infrastructure
- **MySQL**: Event storage
- **Kafka**: Message broker
- **Zookeeper**: Kafka coordination

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Azure VM or similar cloud instance
- Postman for testing

### Environment Setup
1. Clone the repository:
```bash
git clone https://github.com/NedWithNoHead/Runify.git
cd runify
```

2. Create environment files:
```bash
# Create .env in root directory
cat > .env << EOL
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PORT=your_port
EOL
```

3. Build and start services:
```bash
# Build all services
docker compose build

# Start services
docker compose up -d
```

### API Testing

1. Running Stats:
```bash
# Submit running data
POST http://hostname:8080/stats/running
{
    "user_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "duration": 3600,
    "distance": 5000,
    "timestamp": "2024-09-10T09:12:33.001Z"
}

# Get stats
GET http://hostname:8100/stats
```

2. Music Info:
```bash
# Submit music data
POST http://hostname:8080/stats/music
{
    "user_id": "d999f1ee-6c54-4b01-90e6-d701748f0851",
    "song_name": "Run Boy Run",
    "artist": "Woodkid",
    "song_duration": 180,
    "timestamp": "2024-09-10T09:12:33.001Z"
}
```

### Load Testing
JMeter configuration provided for load testing:
- Test Plan: `test_plan.jmx`
- Simulates concurrent users
- Random data generation
- Response validation

## Architecture Details

### Docker Networks
- All services share a common network
- Internal service discovery via container names
- External access via port mapping

### Data Flow
1. Receiver accepts REST requests
2. Messages published to Kafka
3. Storage service consumes and persists data
4. Processing service generates statistics
5. Analyzer provides message queue insights

### Security Notes
- Sensitive data in .env files (not in git)
- Required ports exposed via Azure NSG
- Internal docker network for service communication

## Troubleshooting

### Common Issues
1. Connection Issues:
   - Check if all services are running (`docker compose ps`)
   - Verify port mappings
   - Check Azure NSG rules

2. Database Issues:
   - Check MySQL connection
   - Verify environment variables

3. Kafka Issues:
   - Check Zookeeper status
   - Verify topic creation
   - Check consumer group offsets

## Monitoring
- Service logs: `docker compose logs [service_name]`
- MySQL data: Connect via port 33060
- Kafka topics: Access via port 9092