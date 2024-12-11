import connexion
from connexion import NoContent
import json
import os
import yaml
import logging
import logging.config
import requests
from requests.exceptions import Timeout, ConnectionError
from apscheduler.schedulers.background import BackgroundScheduler
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

def check_services():
    """Periodically check service health"""
    logger.info("Starting periodic service check")
    
    status = {
        "receiver": "Unavailable",
        "storage": "Unavailable",
        "processing": "Unavailable",
        "analyzer": "Unavailable"
    }

    try:
        response = requests.get(
            app_config["services"]["receiver"],
            timeout=app_config["timeout"]["seconds"]
        )
        if response.status_code == 200:
            status["receiver"] = "Healthy"
            logger.info("Receiver is Healthy")
        else:
            logger.error("Receiver returned non-200 response")
    except (Timeout, ConnectionError) as e:
        logger.error(f"Receiver check failed: {str(e)}")

    try:
        response = requests.get(
            app_config["services"]["storage"],
            timeout=app_config["timeout"]["seconds"]
        )
        if response.status_code == 200:
            data = response.json()
            status["storage"] = f"Storage has {data.get('num_running_stats', 0)} runs and {data.get('num_music_info', 0)} songs"
            logger.info("Storage is Healthy")
        else:
            logger.error("Storage returned non-200 response")
    except (Timeout, ConnectionError) as e:
        logger.error(f"Storage check failed: {str(e)}")

    # Check Processing
    try:
        response = requests.get(
            app_config["services"]["processing"],
            timeout=app_config["timeout"]["seconds"]
        )
        if response.status_code == 200:
            data = response.json()
            status["processing"] = f"Processing has {data.get('num_running_stats', 0)} runs and {data.get('num_music_info', 0)} songs"
            logger.info("Processing is Healthy")
        else:
            logger.error("Processing returned non-200 response")
    except (Timeout, ConnectionError) as e:
        logger.error(f"Processing check failed: {str(e)}")

    # Check Analyzer
    try:
        response = requests.get(
            app_config["services"]["analyzer"],
            timeout=app_config["timeout"]["seconds"]
        )
        if response.status_code == 200:
            data = response.json()
            status["analyzer"] = f"Analyzer has {data.get('num_running_stats', 0)} runs and {data.get('num_music_info', 0)} songs"
            logger.info("Analyzer is Healthy")
        else:
            logger.error("Analyzer returned non-200 response")
    except (Timeout, ConnectionError) as e:
        logger.error(f"Analyzer check failed: {str(e)}")

    # Write status to file
    try:
        with open(app_config["datastore"]["filename"], 'w') as f:
            json.dump(status, f, indent=4)
        logger.info("Successfully wrote status to file")
    except Exception as e:
        logger.error(f"Failed to write status file: {str(e)}")

    logger.info("Completed periodic service check")

def get_checks():
    """Get the latest service check results"""
    logger.info("Request for service check status received")
    
    if not os.path.exists(app_config["datastore"]["filename"]):
        logger.error("Status file not found")
        return {"message": "Status not found"}, 404

    try:
        with open(app_config["datastore"]["filename"], 'r') as f:
            status = json.load(f)
        logger.info("Successfully retrieved status")
        return status, 200
    except Exception as e:
        logger.error(f"Error reading status file: {str(e)}")
        return {"message": "Error reading status"}, 500

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        check_services,
        'interval',
        seconds=app_config['schedule']['period_sec']
    )
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/check", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    init_scheduler()
    app.run(host="0.0.0.0", port=8130)