import sqlite3

conn = sqlite3.connect("event_management.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    INSERT INTO admins(admin_id, email, password)
    VALUES (?, ?, ?)
    """, (
        "admin123",
        "admin@gmail.com",
        "college2026"
    ))

    conn.commit()
    print("Admin added successfully!")

except sqlite3.IntegrityError:
    print("Admin already exists!")

conn.close()