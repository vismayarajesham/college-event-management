import sqlite3

conn = sqlite3.connect('event_management.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM events")

events = cursor.fetchall()

for event in events:
    print(event)

conn.close()