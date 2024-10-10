import connexion, json
from connexion import NoContent
from datetime import datetime
import json
import requests
import yaml
import logging
import logging.config
import uuid

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

    header = {"content-type": "application/json"}
    body['trace_id'] = trace_id
    response = requests.post(app_config['running_event']['url'], json=body, headers=header)

    logger.info(f"Returned event running_stats response (Id: {trace_id}) with status {response.status_code}")
    return NoContent, response.status_code


def music_info(body):
    """Forward music data to the storage service"""
    trace_id = str(uuid.uuid4())
    logger.info(f"Received music data with a unique id of {trace_id}")


    header = {"content-type": "application/json"}
    body['trace_id'] = trace_id
    response = requests.post(app_config['music_event']['url'], json=body, headers=header)
    
    logger.info(f"Returned event music_info response (Id: {trace_id}) with status {response.status_code}")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
