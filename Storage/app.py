import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models import Base, RunningData, MusicData
from db import get_db_session, create_tables
import yaml
import logging
import logging.config
from datetime import datetime
import os
import json
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType
from dotenv import load_dotenv
import uuid

# Load .env file
load_dotenv()

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

app_config['datastore']['password'] = os.getenv('MYSQL_ROOT_PASSWORD', app_config['datastore']['password'])
app_config['datastore']['port'] = int(os.getenv('MYSQL_PORT', app_config['datastore']['port']))

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"Connecting to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}")

def get_running_stats(start_timestamp, end_timestamp):
    """ Gets running stats after the timestamp """
    session = get_db_session()
    
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    
    readings = session.query(RunningData).filter(
        and_(RunningData.date_created >= start_timestamp_datetime,
             RunningData.date_created < end_timestamp_datetime)
    )
    
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    
    if results_list:  
        logger.info("Query for Running stats after %s returns %d results" % 
                    (start_timestamp, len(results_list)))
    
    return results_list, 200

def get_music_info(start_timestamp, end_timestamp):
    """ Gets music info after the timestamp """
    session = get_db_session()
    
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    
    readings = session.query(MusicData).filter(
        and_(MusicData.date_created >= start_timestamp_datetime,
             MusicData.date_created < end_timestamp_datetime)
    )
    
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    
    if results_list:
        logger.info("Query for Music info after %s returns %d results" % 
                    (start_timestamp, len(results_list)))
    
    return results_list, 200

def running_stats(body):
    """ Receives running data """
    session = get_db_session()
    rd = RunningData(
        user_id=body['user_id'],
        duration=body['duration'],
        distance=body['distance'],
        timestamp=body['timestamp'],
        trace_id=body.get('trace_id', str(uuid.uuid4()))
    )
    
    session.add(rd)
    session.commit()
    trace_id = rd.trace_id
    session.close()

    logger.info(f"Store event running_stats request with a trace id of {rd.trace_id}")


    return NoContent, 201

def music_info(body):
    """ Receives music data """
    session = get_db_session()
    md = MusicData(
        user_id=body['user_id'],
        song_name=body['song_name'],
        artist=body['artist'],
        song_duration=body['song_duration'],
        timestamp=body['timestamp'],
        trace_id=body.get('trace_id', str(uuid.uuid4()))
    )
    
    session.add(md)
    session.commit()
    trace_id = md.trace_id
    session.close()

    logger.info(f"Store event music_info request with a trace id of {md.trace_id}")

    return NoContent, 201

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config['events']['hostname'], app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    while True:
        try:
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info(f"Consumed message: {msg}")

                payload = msg['payload']

                if msg['type'] == 'running_stats':
                    running_stats(payload)
                elif msg['type'] == 'music_info':
                    music_info(payload)

                consumer.commit_offsets()
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon = True
    t1.start()
    create_tables()
    app.run(host="0.0.0.0", port=8090)
