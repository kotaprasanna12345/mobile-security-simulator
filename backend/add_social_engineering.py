
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

scenarios = [
    {
        "attack_type": "Social Engineering",
        "title": "Fake Technical Support Call",
        "difficulty": "MEDIUM",
        "scenario_text": "Someone calls claiming to be a technician from your phone company. They say your phone has a virus and ask you to install a remote-access app. What should you do?",
        "options": [
            "Install the app immediately",
            "Share your screen and passwords",
            "End the call and contact the company using its official contact details",
            "Give the caller your OTP"
        ],
        "correct_answer": "End the call and contact the company using its official contact details",
        "explanation": "Scammers may impersonate technical support to gain access to your device or accounts. Verify unexpected requests independently.",
        "defence_tip": "Never grant remote access to an unsolicited caller. Contact support through official channels."
    },
    {
        "attack_type": "Social Engineering",
        "title": "Urgent Money Request",
        "difficulty": "MEDIUM",
        "scenario_text": "You receive a message from an unknown number claiming to be your friend. They say they urgently need money and ask you to transfer it immediately. What should you do?",
        "options": [
            "Transfer money without checking",
            "Verify the request by calling your friend using a known number",
            "Share your banking PIN with the sender",
            "Forward the message to all your contacts"
        ],
        "correct_answer": "Verify the request by calling your friend using a known number",
        "explanation": "Attackers can impersonate people you know and use urgency to stop you from checking the facts.",
        "defence_tip": "Verify unexpected financial requests through a separate, trusted communication channel."
    },
    {
        "attack_type": "Social Engineering",
        "title": "Prize Claim Scam",
        "difficulty": "MEDIUM",
        "scenario_text": "A message says you have won a smartphone, but you must pay a processing fee and provide personal information to claim it. What is the safest action?",
        "options": [
            "Pay the fee immediately",
            "Send your identity documents to the sender",
            "Click every link in the message",
            "Avoid paying or sharing information and verify the offer independently"
        ],
        "correct_answer": "Avoid paying or sharing information and verify the offer independently",
        "explanation": "Unexpected prize messages may use excitement to trick people into paying fees or revealing personal information.",
        "defence_tip": "Be cautious of prizes you did not enter to win, especially when payment is demanded."
    },
    {
        "attack_type": "Social Engineering",
        "title": "Impersonating College Staff",
        "difficulty": "MEDIUM",
        "scenario_text": "Someone claiming to be college staff messages you asking for your student portal password to update your records urgently. What should you do?",
        "options": [
            "Send the password because they claim to be staff",
            "Ask for their official identity and verify the request through a trusted college channel",
            "Share your password and OTP together",
            "Post your login details in the class group"
        ],
        "correct_answer": "Ask for their official identity and verify the request through a trusted college channel",
        "explanation": "Attackers may impersonate trusted authorities to obtain account credentials. Legitimate staff should not need your password.",
        "defence_tip": "Never share your password or OTP. Confirm unusual requests with your institution."
    },
    {
        "attack_type": "Social Engineering",
        "title": "Threatening Account Suspension",
        "difficulty": "MEDIUM",
        "scenario_text": "A message claims your account will be permanently deleted in ten minutes unless you click a link and enter your login details. What should you do?",
        "options": [
            "Click the link because the deadline is short",
            "Enter your password to avoid losing the account",
            "Open the official app or website directly and check your account status",
            "Send your OTP to the message sender"
        ],
        "correct_answer": "Open the official app or website directly and check your account status",
        "explanation": "Threats and artificial deadlines are common manipulation tactics used to pressure people into revealing credentials.",
        "defence_tip": "Pause before acting on urgent messages and verify account alerts through official channels."
    }
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(scenarios)")
    columns = {row[1] for row in cursor.fetchall()}

    required = {
        "attack_type", "title", "difficulty", "scenario_text",
        "correct_answer", "explanation", "defence_tip", "options"
    }

    missing = required - columns

    if missing:
        raise Exception(
            "Missing database columns: " + ", ".join(sorted(missing))
        )

    added = 0

    for item in scenarios:
        cursor.execute(
            """
            SELECT COUNT(*) FROM scenarios
            WHERE LOWER(TRIM(title)) = LOWER(TRIM(?))
              AND LOWER(TRIM(attack_type)) = 'social engineering'
            """,
            (item["title"],)
        )

        if cursor.fetchone()[0] > 0:
            print("Already exists:", item["title"])
            continue

        cursor.execute(
            """
            INSERT INTO scenarios (
                attack_type, title, difficulty, scenario_text,
                correct_answer, explanation, defence_tip, options
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["attack_type"],
                item["title"],
                item["difficulty"],
                item["scenario_text"],
                item["correct_answer"],
                item["explanation"],
                item["defence_tip"],
                json.dumps(item["options"])
            )
        )

        added += 1

    conn.commit()
    print(f"\nSocial Engineering setup completed! Added {added} new questions.")

    cursor.execute("""
        SELECT title, difficulty
        FROM scenarios
        WHERE LOWER(TRIM(attack_type)) = 'social engineering'
    """)

    for title, difficulty in cursor.fetchall():
        print(f"- {title} [{difficulty}]")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    conn.close()