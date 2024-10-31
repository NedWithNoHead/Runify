import connexion, json
from connexion import NoContent
from datetime import datetime
import json
import requests
import yaml
import logging
import logging.config
import uuid
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def running_stats(body):
    """Forward running data to the storage service"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Received running data with a unique id of {trace_id}")

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()

    msg = {
        "type": "running_stats",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg['payload']['trace_id'] = trace_id
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event running_stats response (Id: {trace_id}) with status (Id: {trace_id} with status 201)")
    return NoContent, 201


def music_info(body):
    """Forward music data to the storage service"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Received music data with a unique id of {trace_id}")

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()

    msg = {
        "type": "music_info",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg['payload']['trace_id'] = trace_id
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event music_info response (Id: {trace_id}) with status (Id: {trace_id} with status 201)")
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
