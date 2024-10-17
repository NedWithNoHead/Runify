import mysql.connector
import yaml
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Override config with environment variables
app_config['datastore']['password'] = os.getenv('MYSQL_ROOT_PASSWORD', app_config['datastore']['password'])
app_config['datastore']['port'] = int(os.getenv('MYSQL_PORT', app_config['datastore']['port']))

try:
    print(f"Attempting to connect to MySQL...")
    db_connection = mysql.connector.connect(
        host=app_config['datastore']['hostname'],
        user=app_config['datastore']['user'],
        password=app_config['datastore']['password'],
        database=app_config['datastore']['db'],
        port=app_config['datastore']['port']
    )
    print("Successfully connected to MySQL.")

    db_cursor = db_connection.cursor()

    # Drop tables
    drop_tables_query = '''
        DROP TABLE IF EXISTS running_data, music_data
    '''
    print(f"Executing SQL: {drop_tables_query}")
    db_cursor.execute(drop_tables_query)
    print("Tables dropped successfully.")

    db_connection.commit()
    print("Changes committed.")

    # Verify tables are dropped
    db_cursor.execute("SHOW TABLES")
    tables = db_cursor.fetchall()
    print(f"Remaining tables in the database: {tables}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if 'db_connection' in locals() and db_connection.is_connected():
        db_cursor.close()
        db_connection.close()
        print("MySQL connection closed.")