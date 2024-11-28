import connexion
from connexion import NoContent
import json
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import os
from datetime import datetime
import time
from flask_cors import CORS

# Load configuration files from the same directory as the application
app_conf_file = "app_conf.yml"
log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def get_anomalies(anomaly_type=None):
    """Get anomalies from the datastore"""
    logger.info(f"Request for anomalies with type {anomaly_type}")
    
    if not os.path.exists(app_config["datastore"]["filename"]):
        logger.error("Datastore file not found")
        return {"message": "Statistics do not exist"}, 404

    with open(app_config["datastore"]["filename"], 'r') as f:
        anomalies = json.load(f)

    if anomaly_type:
        anomalies = [a for a in anomalies if a["anomaly_type"] == anomaly_type]
    
    # Sort by timestamp descending
    anomalies.sort(key=lambda x: x["timestamp"], reverse=True)
    
    logger.debug(f"Returning {len(anomalies)} anomalies")
    return anomalies, 200

def add_anomaly(anomaly):
    """Add a new anomaly to the datastore"""
    
    # Create file if it doesn't exist
    if not os.path.exists(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"], 'w') as f:
            json.dump([], f)
    
    # Read current anomalies
    with open(app_config["datastore"]["filename"], 'r') as f:
        anomalies = json.load(f)
    
    # Add new anomaly
    anomalies.append(anomaly)
    
    # Write back to file
    with open(app_config["datastore"]["filename"], 'w') as f:
        json.dump(anomalies, f, indent=2)
    
    logger.info(f"Added new anomaly: {anomaly}")

def process_messages():
    """Process messages from Kafka"""
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    max_retries = 10
    current_retry = 0
    
    logger.info(f"Connecting to Kafka at {hostname}")
    
    while current_retry < max_retries:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            
            consumer = topic.get_simple_consumer(
                consumer_group=b'anomaly_detector_group',
                reset_offset_on_start=False,
                auto_offset_reset=OffsetType.LATEST
            )
            
            logger.info("Successfully connected to Kafka")
            break
        except Exception as e:
            logger.error(f"Connection to Kafka failed: {str(e)}")
            time.sleep(5)
            current_retry += 1
    
    if current_retry == max_retries:
        logger.error("Failed to connect to Kafka after maximum retries")
        return
    
    # Process messages
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Received event: {msg}")
        
        payload = msg["payload"]
        event_type = msg["type"]
        
        # Check for anomalies based on event type
        if event_type == "running_stats":
            # Check distance
            if payload["distance"] > app_config["thresholds"]["running"]["max_distance"]:
                anomaly = {
                    "event_id": payload["user_id"],
                    "trace_id": payload["trace_id"],
                    "event_type": "running_stats",
                    "anomaly_type": "LongRun",
                    "description": f"Run distance of {payload['distance']}m exceeds maximum threshold of {app_config['thresholds']['running']['max_distance']}m",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                add_anomaly(anomaly)
            
            # Check duration
            if payload["duration"] < app_config["thresholds"]["running"]["min_duration"]:
                anomaly = {
                    "event_id": payload["user_id"],
                    "trace_id": payload["trace_id"],
                    "event_type": "running_stats",
                    "anomaly_type": "ShortRun",
                    "description": f"Run duration of {payload['duration']}s is below minimum threshold of {app_config['thresholds']['running']['min_duration']}s",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                add_anomaly(anomaly)
                
        elif event_type == "music_info":
            # Check song duration
            if payload["song_duration"] > app_config["thresholds"]["music"]["max_duration"]:
                anomaly = {
                    "event_id": payload["user_id"],
                    "trace_id": payload["trace_id"],
                    "event_type": "music_info",
                    "anomaly_type": "LongSong",
                    "description": f"Song duration of {payload['song_duration']}s exceeds maximum threshold of {app_config['thresholds']['music']['max_duration']}s",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                add_anomaly(anomaly)
            
            if payload["song_duration"] < app_config["thresholds"]["music"]["min_duration"]:
                anomaly = {
                    "event_id": payload["user_id"],
                    "trace_id": payload["trace_id"],
                    "event_type": "music_info",
                    "anomaly_type": "ShortSong",
                    "description": f"Song duration of {payload['song_duration']}s is below minimum threshold of {app_config['thresholds']['music']['min_duration']}s",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                add_anomaly(anomaly)
        
        consumer.commit_offsets()

# Create Flask app
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/anomaly", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    # Start message processing in a separate thread
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    
    # Log configuration on startup
    logger.info("Starting Anomaly Detector Service")
    logger.info(f"Running thresholds: max_distance={app_config['thresholds']['running']['max_distance']}m, min_duration={app_config['thresholds']['running']['min_duration']}s")
    logger.info(f"Music thresholds: max_duration={app_config['thresholds']['music']['max_duration']}s, min_duration={app_config['thresholds']['music']['min_duration']}s")
    
    app.run(host="0.0.0.0", port=8120)