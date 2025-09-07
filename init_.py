import sqlite3

conn = sqlite3.connect("init.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade REAL NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ Database created with ID field.")
