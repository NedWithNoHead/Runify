import sys
import yaml
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

app_config['datastore']['password'] = os.getenv('MYSQL_ROOT_PASSWORD', app_config['datastore']['password'])
app_config['datastore']['port'] = int(os.getenv('MYSQL_PORT', app_config['datastore']['port']))

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

SessionFactory = sessionmaker(bind=DB_ENGINE)
Session = scoped_session(SessionFactory)

def get_db_session():
    return Session()

def create_tables():
    Base.metadata.create_all(DB_ENGINE)
    print("Tables created successfully.")

def drop_tables():
    Base.metadata.drop_all(DB_ENGINE)
    print("Tables dropped successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    create_tables()