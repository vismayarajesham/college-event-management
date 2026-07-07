import sqlite3

conn = sqlite3.connect('event_management.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    event_name TEXT
)
''')

conn.commit()
conn.close()

print("Registrations Table Created")