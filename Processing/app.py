import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from datetime import datetime
import os
import traceback

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_stats():
    logger.info("Request for statistics has started")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, app_config['datastore']['filename'])
    
    if not os.path.exists(file_path): 
        logger.error(f"Statistics do not exist at {file_path}")
        return {"message": "Statistics do not exist"}, 404
    
    with open(file_path, 'r') as f: 
        stats = json.load(f)
    
    logger.info(f"Statistics retrieved: {stats}")
    logger.info("Request for statistics has completed")
    
    return stats, 200

def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, app_config['datastore']['filename'])
    
    logger.info(f"Checking for stats file at: {file_path}")
    
    if not os.path.exists(file_path):
        stats = {
            "num_running_stats": 0,
            "num_music_info": 0,
            "max_distance": 0,
            "max_duration": 0,
            "avg_run_duration": 0,
            "avg_song_duration": 0,
            "last_updated": "2000-01-01T00:00:00Z"
        }
        with open(file_path, 'w') as f:
            json.dump(stats, f, indent=4)
        logger.info("Created new stats file")
    else:
        with open(file_path, 'r') as f:
            stats = json.load(f)

        stats.setdefault('avg_run_duration', 0)
        stats.setdefault('avg_song_duration', 0)
    
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        running_response = requests.get(
            f"{app_config['eventstore']['url']}/stats/running",
            params={'start_timestamp': stats['last_updated'], 'end_timestamp': current_datetime}
        )
        running_response.raise_for_status()
        running_data = running_response.json()
        
        if running_data:
            new_run_count = len(running_data)
            total_duration = sum(run['duration'] for run in running_data)
            
            # total count
            stats['num_running_stats'] += new_run_count
            
            # max values
            stats['max_distance'] = max(stats['max_distance'], max(run['distance'] for run in running_data))
            stats['max_duration'] = max(stats['max_duration'], max(run['duration'] for run in running_data))
            
            # average duration
            current_total = stats['avg_run_duration'] * (stats['num_running_stats'] - new_run_count)
            new_total = current_total + total_duration
            stats['avg_run_duration'] = new_total / stats['num_running_stats']
        
        logger.info(f"Processed {len(running_data)} running stats")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve running stats: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing running data: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
    
    try:
        music_response = requests.get(
            f"{app_config['eventstore']['url']}/stats/music",
            params={'start_timestamp': stats['last_updated'], 'end_timestamp': current_datetime}
        )
        music_response.raise_for_status()
        music_data = music_response.json()
        
        if music_data:
            new_music_count = len(music_data)
            total_song_duration = sum(song['song_duration'] for song in music_data)
            
            #  total count
            stats['num_music_info'] += new_music_count
            
            #  average song duration
            current_total = stats['avg_song_duration'] * (stats['num_music_info'] - new_music_count)
            new_total = current_total + total_song_duration
            stats['avg_song_duration'] = new_total / stats['num_music_info']
        
        logger.info(f"Processed {len(music_data)} music info records")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve music info: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing music data: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
    
    stats['last_updated'] = current_datetime
    
    with open(file_path, 'w') as f:  
        json.dump(stats, f, indent=4)
    
    logger.info(f"Updated stats: {stats}")
    logger.info("End Periodic Processing")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(host="0.0.0.0",port=8100)