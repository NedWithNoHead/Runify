import connexion
from connexion import NoContent
import json
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from dotenv import load_dotenv
from flask_cors import CORS

# Load configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_running_stats(index):
    """ Get Running Stats in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                       consumer_timeout_ms=1000)
    
    logger.info(f"Retrieving running stats at index {index}")
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg["type"] == "running_stats":
                if count == index:
                    return msg["payload"], 200
                count += 1
                
    except:
        logger.error("No more messages found")
        
    logger.error(f"Could not find running stats at index {index}")
    return {"message": "Not Found"}, 404

def get_music_info(index):
    """ Get Music Info in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                       consumer_timeout_ms=1000)
    
    logger.info(f"Retrieving music info at index {index}")
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg["type"] == "music_info":
                if count == index:
                    return msg["payload"], 200
                count += 1
                
    except:
        logger.error("No more messages found")
        
    logger.error(f"Could not find music info at index {index}")
    return {"message": "Not Found"}, 404

def get_stats():
    """ Get Stats from History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                       consumer_timeout_ms=1000)
    
    logger.info("Retrieving stats")
    stats = {
        "num_running_stats": 0,
        "num_music_info": 0
    }
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg["type"] == "running_stats":
                stats["num_running_stats"] += 1
            elif msg["type"] == "music_info":
                stats["num_music_info"] += 1
                
    except:
        logger.error("No more messages found")
        
    logger.info(f"Stats: {stats}")
    return stats, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8110)