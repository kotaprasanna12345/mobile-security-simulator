
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "data", "simulator.db")
)

QUESTION_TITLE = "Fake Bluetooth Headphones"

CORRECT_ANSWER = (
    "Verify the device name and pairing information before connecting"
)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT scenario_id, title, attack_type
        FROM scenarios
        WHERE LOWER(TRIM(title)) = LOWER(TRIM(?))
          AND LOWER(attack_type) LIKE '%bluetooth%'
    """, (QUESTION_TITLE,))

    question = cursor.fetchone()

    if question is None:
        print("ERROR: Bluetooth question not found.")
        print("Database path:", DB_PATH)

    else:
        scenario_id = question[0]

        cursor.execute("""
            UPDATE scenarios
            SET correct_answer = ?
            WHERE scenario_id = ?
        """, (CORRECT_ANSWER, scenario_id))

        conn.commit()

        cursor.execute("""
            SELECT title, correct_answer
            FROM scenarios
            WHERE scenario_id = ?
        """, (scenario_id,))

        result = cursor.fetchone()

        print("\nSUCCESS: Question updated and verified!")
        print("Question:", result[0])
        print("Correct answer:", result[1])
        print("Database:", DB_PATH)

finally:
    conn.close()