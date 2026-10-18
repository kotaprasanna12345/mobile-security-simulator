
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

scenarios = [
    {
        "attack_type": "Malicious Link",
        "title": "Fake Delivery Tracking Link",
        "difficulty": "MEDIUM",
        "scenario_text": "You receive an unexpected SMS claiming your parcel is delayed. A link asks you to enter your card details to reschedule delivery. What should you do?",
        "options": [
            "Enter your card details immediately",
            "Forward the link to friends",
            "Check the delivery through the courier's official website or app",
            "Download any file the page offers"
        ],
        "correct_answer": "Check the delivery through the courier's official website or app",
        "explanation": "Unexpected delivery messages may use fake links to collect financial information. Verify delivery details through a trusted channel.",
        "defence_tip": "Avoid payment links in unexpected messages. Check tracking details through the courier's official service."
    },
    {
        "attack_type": "Malicious Link",
        "title": "Lookalike Website Address",
        "difficulty": "MEDIUM",
        "scenario_text": "A link claims to open your bank website, but the address contains a misspelled bank name and extra characters. What is the safest action?",
        "options": [
            "Enter your banking password",
            "Avoid the link and access the bank through its verified official address",
            "Share the link with your contacts",
            "Ignore the unusual spelling"
        ],
        "correct_answer": "Avoid the link and access the bank through its verified official address",
        "explanation": "Attackers may use lookalike domains to make fake websites appear legitimate and steal credentials.",
        "defence_tip": "Check domain names carefully and use bookmarks or the bank's official app."
    },
    {
        "attack_type": "Malicious Link",
        "title": "Unexpected File Download",
        "difficulty": "MEDIUM",
        "scenario_text": "A message from an unknown sender says you must open a link to view an important document. The website starts downloading an unfamiliar APK file. What should you do?",
        "options": [
            "Install the APK to view the document",
            "Grant every permission requested",
            "Forward the APK to other people",
            "Cancel the download and avoid installing the unknown file"
        ],
        "correct_answer": "Cancel the download and avoid installing the unknown file",
        "explanation": "Unexpected APK downloads can contain malware. A document link should not automatically be trusted just because its message sounds important.",
        "defence_tip": "Do not install unexpected app files from links or unknown websites."
    },
    {
        "attack_type": "Malicious Link",
        "title": "Fake Account Verification",
        "difficulty": "MEDIUM",
        "scenario_text": "A social media message warns that your account will be suspended unless you verify your password through a link. What should you do?",
        "options": [
            "Enter your password to prevent suspension",
            "Send your password to the sender",
            "Open the official app directly and check for account alerts",
            "Share your OTP with the message sender"
        ],
        "correct_answer": "Open the official app directly and check for account alerts",
        "explanation": "Fake verification links may lead to phishing pages designed to steal account credentials.",
        "defence_tip": "Verify account warnings inside the official app or website instead of following unexpected links."
    },
    {
        "attack_type": "Malicious Link",
        "title": "Suspicious QR Code Link",
        "difficulty": "MEDIUM",
        "scenario_text": "You scan a QR code on a public poster. The website it opens asks for your email password and an OTP to claim a reward. What is the safest response?",
        "options": [
            "Enter the password and OTP",
            "Stop and close the page without sharing sensitive information",
            "Share the page with your friends",
            "Disable phone security to continue"
        ],
        "correct_answer": "Stop and close the page without sharing sensitive information",
        "explanation": "QR codes can redirect users to phishing websites. A QR code does not guarantee that the destination is safe.",
        "defence_tip": "Preview the destination URL and avoid entering sensitive information on unverified pages."
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
              AND LOWER(TRIM(attack_type)) = 'malicious link'
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
    print(f"\nMalicious Link setup completed! Added {added} new questions.")

    cursor.execute("""
        SELECT title, difficulty
        FROM scenarios
        WHERE LOWER(TRIM(attack_type)) = 'malicious link'
    """)

    for title, difficulty in cursor.fetchall():
        print(f"- {title} [{difficulty}]")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    conn.close()