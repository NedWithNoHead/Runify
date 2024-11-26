import connexion, json
from connexion import NoContent
from datetime import datetime
import json
import requests
import yaml
import logging
import logging.config
import uuid
import time
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

kafka_client = None
kafka_topic = None
kafka_producer = None

def get_kafka_client():
    """Get or create Kafka client with retry logic"""
    global kafka_client, kafka_topic, kafka_producer
    
    if kafka_client is None:
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to connect to Kafka \
                            (attempt {retry_count + 1}/{max_retries})")
                kafka_client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
                kafka_topic = kafka_client.topics[str.encode(app_config['events']['topic'])]
                kafka_producer = kafka_topic.get_sync_producer()
                logger.info("Successfully connected to Kafka")
                return kafka_producer
            except Exception as e:
                logger.error(f"Failed to connect to Kafka: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to connect to Kafka after maximum retries")
    
    return kafka_producer

def running_stats(body):
    """Forward running data to the storage service"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Received running data with a unique id of {trace_id}")

    try:
        producer = get_kafka_client()
        
        msg = {
            "type": "running_stats",
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body,
        }
        msg['payload']['trace_id'] = trace_id
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        
        logger.info(f"Returned event running_stats response (Id: {trace_id}) with status 201")
        return NoContent, 201
    except Exception as e:
        logger.error(f"Failed to process running stats: {str(e)}")
        return {"message": "Internal Server Error"}, 500

def music_info(body):
    """Forward music data to the storage service"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Received music data with a unique id of {trace_id}")

    try:
        producer = get_kafka_client()
        
        msg = {
            "type": "music_info",
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body,
        }
        msg['payload']['trace_id'] = trace_id
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        
        logger.info(f"Returned event music_info response (Id: {trace_id}) with status 201")
        return NoContent, 201
    except Exception as e:
        logger.error(f"Failed to process music info: {str(e)}")
        return {"message": "Internal Server Error"}, 500

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    try:
        producer = get_kafka_client()
        logger.info("Kafka producer initialized successfully at startup")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer at startup: {str(e)}")
    
    app.run(host="0.0.0.0", port=8080)