import sqlite3

conn = sqlite3.connect('event_management.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT,
    event_type TEXT,
    event_time TEXT,
    min_members INTEGER,
    max_members INTEGER
)
''')

conn.commit()
conn.close()

print("Events Table Created")