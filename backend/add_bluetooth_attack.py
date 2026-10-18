import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

CORRECT_ANSWER = (
    "Verify the device name and pairing information before connecting"
)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        UPDATE scenarios
        SET correct_answer = ?
        WHERE LOWER(TRIM(title)) = LOWER(?)
          AND LOWER(TRIM(attack_type)) LIKE '%bluetooth%'
    """, (
        CORRECT_ANSWER,
        "Fake Bluetooth Headphones"
    ))

    if cursor.rowcount == 0:
        print("❌ Matching Bluetooth question not found.")
        print("Check the exact title and attack_type in the database.")
        conn.rollback()
    else:
        conn.commit()
        print("✅ Bluetooth answer updated successfully!")

    cursor.execute("""
        SELECT title, attack_type, correct_answer
        FROM scenarios
        WHERE LOWER(TRIM(title)) = LOWER(?)
    """, ("Fake Bluetooth Headphones",))

    for row in cursor.fetchall():
        print("\nTitle:", row[0])
        print("Category:", row[1])
        print("Correct Answer:", row[2])

finally:
    conn.close()