import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
    CREATE TABLE running_data (
        id INTEGER PRIMARY KEY ASC, 
        user_id VARCHAR(250) NOT NULL,
        duration INTEGER NOT NULL,
        distance INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL
    )
''')
c.execute('''
    CREATE TABLE music_data (
        id INTEGER PRIMARY KEY ASC, 
        user_id VARCHAR(250) NOT NULL,
        song_name VARCHAR(250) NOT NULL,
        artist VARCHAR(250) NOT NULL,
        song_duration INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL
    )
''')


conn.commit()
conn.close()