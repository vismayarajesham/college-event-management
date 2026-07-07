import sqlite3

conn = sqlite3.connect('event_management.db')

cursor = conn.cursor()

cursor.execute("SELECT * FROM registrations")

print(cursor.fetchall())

conn.close()