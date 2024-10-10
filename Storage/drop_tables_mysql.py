import mysql.connector

db_connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "events"
)

db_cursor = db_connection.cursor()

db_cursor.execute('''
    DROP TABLE IF EXISTS running_data, music_data
''')

db_connection.commit()
db_connection.close()