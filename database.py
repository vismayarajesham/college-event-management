import sqlite3

conn = sqlite3.connect('event_management.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    password TEXT
)
''')

conn.commit()
conn.close()

print("Students Table Created")