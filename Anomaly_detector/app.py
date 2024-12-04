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

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
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
    
    anomalies.sort(key=lambda x: x["timestamp"], reverse=True)
    
    logger.debug(f"Returning {len(anomalies)} anomalies")
    return anomalies, 200

def add_anomaly(anomaly):
    """Add a new anomaly to the datastore"""
    
    if not os.path.exists(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"], 'w') as f:
            json.dump([], f)
    
    with open(app_config["datastore"]["filename"], 'r') as f:
        anomalies = json.load(f)
    
    anomalies.append(anomaly)
    
    with open(app_config["datastore"]["filename"], 'w') as f:
        json.dump(anomalies, f, indent=2)
    
    logger.info(f"Added new anomaly: {anomaly}")

def process_messages():
    message_batch_size = 1000  
    batch_timeout = 300        
    retry_count = 0
    max_retries = 3
    consumer = None
    
    hostname = "%s:%d" % (app_config['events']['hostname'], app_config['events']['port'])
    logger.info("Starting message processing service")
    logger.info(f"Connecting to Kafka at {hostname}")
    
    while True:
        message_count = 0
        start_time = time.time()
        
        try:
            if consumer is None:
                logger.info("Attempting to establish Kafka connection")
                client = KafkaClient(hosts=hostname)
                topic = client.topics[str.encode(app_config["events"]["topic"])]
                consumer = topic.get_simple_consumer(
                    consumer_group=b'anomaly_detector_group',
                    reset_offset_on_start=False,
                    auto_offset_reset=OffsetType.LATEST
                )
                logger.info("Successfully connected to Kafka")
                retry_count = 0 
            
            for msg in consumer:
                try:
                    message_count += 1
                    current_time = time.time()
                    if message_count >= message_batch_size or (current_time - start_time) > batch_timeout:
                        logger.info(f"Taking a break after processing {message_count} messages")
                        time.sleep(1)  
                        message_count = 0
                        start_time = current_time
                    
                    msg_str = msg.value.decode('utf-8')
                    msg = json.loads(msg_str)
                    logger.debug(f"Received event: {msg}")  
                    
                    payload = msg["payload"]
                    event_type = msg["type"]
                    
                    if event_type == "running_stats":
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
                            logger.info(f"Detected LongRun anomaly: {payload['user_id']}")
                        
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
                            logger.info(f"Detected ShortRun anomaly: {payload['user_id']}")
                    
                    elif event_type == "music_info":
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
                            logger.info(f"Detected LongSong anomaly: {payload['user_id']}")
                        
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
                            logger.info(f"Detected ShortSong anomaly: {payload['user_id']}")
                    
                    consumer.commit_offsets()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {e}")
                    continue  
                except Exception as e:
                    logger.error(f"Error processing individual message: {e}")
                    continue 
            
        except Exception as e:
            logger.error(f"Error in message processing loop: {str(e)}")
            consumer = None  
            retry_count += 1
            
            if retry_count >= max_retries:
                logger.error("Max retries reached, entering cooldown period")
                time.sleep(60)  
                retry_count = 0
            else:
                sleep_time = min(5 * (2 ** retry_count), 30)  
                logger.info(f"Retrying in {sleep_time} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(sleep_time)

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/anomaly", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    
    logger.info("Starting Anomaly Detector Service")
    logger.info(f"Running thresholds: max_distance={app_config['thresholds']['running']['max_distance']}m, min_duration={app_config['thresholds']['running']['min_duration']}s")
    logger.info(f"Music thresholds: max_duration={app_config['thresholds']['music']['max_duration']}s, min_duration={app_config['thresholds']['music']['min_duration']}s")
    
    app.run(host="0.0.0.0", port=8120)