import sqlite3

conn = sqlite3.connect('event_management.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM registrations")

conn.commit()
conn.close()

print("All registrations deleted")