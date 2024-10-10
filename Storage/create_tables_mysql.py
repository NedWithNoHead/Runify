import mysql.connector
import yaml
import time

# Load configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

max_retries = 5
retry_delay = 5  # seconds

for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to MySQL (Attempt {attempt + 1}/{max_retries})...")
        db_conn = mysql.connector.connect(
            host=app_config['datastore']['hostname'],
            user=app_config['datastore']['user'],
            password=app_config['datastore']['password'],
            database=app_config['datastore']['db'],
            port=app_config['datastore']['port']
        )
        print("Successfully connected to MySQL.")
        break
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries reached. Exiting.")
            raise

db_cursor = db_conn.cursor()

# Create tables
try:
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS running_data (
            id INT NOT NULL AUTO_INCREMENT,
            user_id VARCHAR(250) NOT NULL,
            duration INTEGER NOT NULL,
            distance INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            trace_id VARCHAR(100) NOT NULL,
            date_created VARCHAR(100) NOT NULL,
            PRIMARY KEY (id)
        )
    ''')

    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS music_data (
            id INT NOT NULL AUTO_INCREMENT,
            user_id VARCHAR(250) NOT NULL,
            song_name VARCHAR(250) NOT NULL,
            artist VARCHAR(250) NOT NULL,
            song_duration INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            trace_id VARCHAR(100) NOT NULL,
            date_created VARCHAR(100) NOT NULL,
            PRIMARY KEY (id)
        )
    ''')

    db_conn.commit()
    print("Tables created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating tables: {err}")
finally:
    db_cursor.close()
    db_conn.close()
    print("MySQL connection closed.")