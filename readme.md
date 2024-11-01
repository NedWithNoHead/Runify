# Runify - Event Processing System

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Azure Setup](#azure-setup)
- [Installation](#installation)
- [Services](#services)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)

## Overview
Runify is a microservices-based system for processing running and music data, featuring:
- REST APIs for synchronous communication
- Kafka for asynchronous messaging
- MySQL for persistent storage
- Docker for containerization

## Architecture
### System Components
```text
┌────────────┐    ┌────────────┐    ┌─────────────┐
│  Receiver  │───>│   Kafka    │<───│   Storage   │
│ (Port 8080)│    │(Internal)  │    │ (Internal)  │
└────────────┘    └────────────┘    └─────────────┘
       ▲                                   ▲
       │                                   │
       │          ┌────────────┐           │
       └──────────│  MySQL DB  │───────────┘
                  │(Internal)  │
                  └────────────┘
                        ▲
                        │
     ┌──────────────────┴──────────────────┐
     │                                     │
┌────────────┐                      ┌─────────────┐
│ Processing │                      │  Analyzer   │
│(Port 8100) │                      │(Port 8110)  │
└────────────┘                      └─────────────┘
```

### Data Flow
1. External clients send data to Receiver (8080)
2. Receiver publishes to Kafka
3. Storage service consumes and persists data
4. Processing service (8100) generates statistics
5. Analyzer monitors message flow

## Prerequisites
- Azure subscription
- Local development environment with:
  - Python 3.9+
  - Docker and Docker Compose
  - Git

## Azure Setup

### 1. Create VM
1. Create a B2s (2 vcpus, 4 GiB memory) Ubuntu 22.04 VM
2. Enable SSH access
3. Configure DNS name
4. Open required ports in Network Security Group:
   ```
   Port 22 (SSH)
   Port 8080 (Receiver Service)
   Port 8100 (Processing Service)
   ```
   Note: Other ports remain internal to the system for security.

### 2. Install Docker
Follow the official documentation:
[https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)

```bash
# After installation, run:
sudo usermod -aG docker ${USER}
# Log out and log back in
```

## Installation

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

## Services

### Service Details

#### Receiver (Port 8080)
- Accepts POST requests for running and music data
- Validates incoming data
- Publishes to Kafka topic

Example request:
```bash
curl -X POST http://hostname:8080/stats/running \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "duration": 3600,
    "distance": 5000,
    "timestamp": "2024-09-10T09:12:33.001Z"
}'

curl -X POST http://hostname:8080/stats/music \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "d999f1ee-6c54-4b01-90e6-d701748f0851",
    "song_name": "Run Boy Run",
    "artist": "Woodkid",
    "song_duration": 180,
    "timestamp": "2024-09-10T09:12:33.001Z"
}'
```

#### Storage (Internal)
- Consumes Kafka messages
- Stores data in MySQL
- Provides data retrieval for Processing service

#### Processing (Port 8100)
- Generates statistics every 30 seconds
- Stores stats in data.json
- Provides aggregated statistics

Example request:
```bash
curl http://hostname:8100/stats
```

#### Analyzer (Internal)
- Provides message queue insights
- Allows access to historical events

## Configuration

### Required Configuration Files
1. `.env` file in root directory:
```env
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PORT=your_port
```

2. Add to `.gitignore`:
```gitignore
**/.env
**/data.json
**/__pycache__/
**/app.log
docker/
```

## Running the System

1. Initial startup:
```bash
docker compose up -d
```

2. Check service status:
```bash
docker compose ps
docker compose logs -f
```

3. Monitor specific service:
```bash
docker compose logs -f <service-name>
```

## Testing

### API Testing
1. Test Receiver endpoints (Port 8080):
```bash
# Submit running data
curl -X POST http://hostname:8080/stats/running \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "duration": 3600,
    "distance": 5000,
    "timestamp": "2024-09-10T09:12:33.001Z"
}'

# Submit music data
curl -X POST http://hostname:8080/stats/music \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "d999f1ee-6c54-4b01-90e6-d701748f0851",
    "song_name": "Run Boy Run",
    "artist": "Woodkid",
    "song_duration": 180,
    "timestamp": "2024-09-10T09:12:33.001Z"
}'
```

2. Check Processing stats (Port 8100):
```bash
curl http://hostname:8100/stats
```

### Load Testing
JMeter test plan provided in `tests/` directory.

## Troubleshooting

### Common Issues
1. Service Logs:
```bash
docker compose logs <service-name>
```

2. Container Status:
```bash
docker compose ps
```

3. Network Issues:
```bash
docker network ls
docker network inspect runify-network
```

## Version History

### v1.1-lab8 (2024-10-31)
- ✅ All microservices functional in Docker containers
- ✅ Kafka messaging system operational
- ✅ MySQL database integration complete
- ✅ Processing service stats tracking working
- ✅ Inter-service communication established
- ✅ Docker networking configured