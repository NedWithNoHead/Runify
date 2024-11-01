# create_tables_mysql.py
import mysql.connector
import yaml
import time
import os
from dotenv import load_dotenv
import sys

def create_tables_mysql(is_docker=False):
    # Load .env file
    load_dotenv()
    
    # Print environment variables (be careful with sensitive info)
    print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
    print(f"MYSQL_ROOT_PASSWORD: {'*' * len(os.getenv('MYSQL_ROOT_PASSWORD', ''))}")
    
    # Load configuration
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    
    # Override config with environment variables
    app_config['datastore']['password'] = os.getenv('MYSQL_ROOT_PASSWORD', app_config['datastore']['password'])
    # app_config['datastore']['port'] = int(os.getenv('MYSQL_PORT', app_config['datastore']['port']))
    
    # Use localhost if running locally
    if not is_docker:
        app_config['datastore']['hostname'] = 'localhost'
    
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
            print(f"Connected to database: {db_conn.database}")
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

    try:
        # Ensure we're using the correct database
        db_cursor.execute(f"USE {app_config['datastore']['db']}")
        print(f"Using database: {app_config['datastore']['db']}")
        
        for table_creation_sql in [
            '''CREATE TABLE IF NOT EXISTS running_data (
                id INT NOT NULL AUTO_INCREMENT,
                user_id VARCHAR(250) NOT NULL,
                duration INTEGER NOT NULL,
                distance INTEGER NOT NULL,
                timestamp VARCHAR(100) NOT NULL,
                trace_id VARCHAR(100) NOT NULL,
                date_created VARCHAR(100) NOT NULL,
                PRIMARY KEY (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS music_data (
                id INT NOT NULL AUTO_INCREMENT,
                user_id VARCHAR(250) NOT NULL,
                song_name VARCHAR(250) NOT NULL,
                artist VARCHAR(250) NOT NULL,
                song_duration INTEGER NOT NULL,
                timestamp VARCHAR(100) NOT NULL,
                trace_id VARCHAR(100) NOT NULL,
                date_created VARCHAR(100) NOT NULL,
                PRIMARY KEY (id)
            )'''
        ]:
            try:
                print(f"Executing SQL: {table_creation_sql}")
                db_cursor.execute(table_creation_sql)
                print(f"SQL executed successfully")
            except mysql.connector.Error as err:
                print(f"Error executing SQL: {err}")
        
        db_conn.commit()
        print("Tables created successfully.")
        
        # Check if tables were actually created
        db_cursor.execute("SHOW TABLES")
        tables = db_cursor.fetchall()
        print(f"Tables in the database: {tables}")
        
    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")
        raise err
    finally:
        db_cursor.close()
        db_conn.close()
        print("MySQL connection closed.")

if __name__ == "__main__":
    # When run directly, use localhost
    create_tables_mysql(is_docker=False)