import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models import Base, RunningData, MusicData
from db import get_db_session
import yaml
import logging
import logging.config
from datetime import datetime

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

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
        trace_id=body['trace_id']
    )
    
    session.add(rd)
    session.commit()
    session.close()

    logger.info(f"Stored event running_stats request with a trace id of {body['trace_id']}")
    
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
        trace_id=body['trace_id']
    )
    
    session.add(md)
    session.commit()
    session.close()

    logger.info(f"Stored event music_info request with a trace id of {body['trace_id']}")

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)