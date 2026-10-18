
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

scenarios = [
    {
        "attack_type": "Credential Theft",
        "title": "Fake Bank Login Page",
        "difficulty": "HARD",
        "scenario_text": "You receive a message claiming your bank account will be blocked today. Its link opens a login page asking for your banking username and password. What should you do?",
        "options": [
            "Enter your credentials immediately",
            "Use the link because the message looks urgent",
            "Close the page and verify the alert using the bank's official app or website",
            "Send your password to the message sender"
        ],
        "correct_answer": "Close the page and verify the alert using the bank's official app or website",
        "explanation": "Urgent messages with login links may be phishing attempts designed to steal credentials. Verify account alerts through a trusted official channel.",
        "defence_tip": "Never log in through unexpected message links. Use the official bank app or type the verified website address yourself."
    },
    {
        "attack_type": "Credential Theft",
        "title": "Unexpected OTP Request",
        "difficulty": "HARD",
        "scenario_text": "Someone calls claiming to be customer support and asks you to read out an OTP to prevent your account from being suspended. What should you do?",
        "options": [
            "Share the OTP to protect your account",
            "Share the OTP only if the caller knows your name",
            "Ask the caller to send another OTP",
            "Do not share the OTP and contact the service through an official channel"
        ],
        "correct_answer": "Do not share the OTP and contact the service through an official channel",
        "explanation": "An OTP can authorize a login or transaction. Fraudsters may impersonate support staff to obtain it.",
        "defence_tip": "Never disclose OTPs, PINs, or verification codes to callers or message senders."
    },
    {
        "attack_type": "Credential Theft",
        "title": "Suspicious Password Reset Email",
        "difficulty": "HARD",
        "scenario_text": "You receive a password-reset email for an account even though you did not request one. The email contains a link to confirm your identity. What is the safest action?",
        "options": [
            "Open the link and enter your current password",
            "Ignore the unexpected link and check your account through its official app or website",
            "Reply with your password to confirm ownership",
            "Forward the email to everyone in your contacts"
        ],
        "correct_answer": "Ignore the unexpected link and check your account through its official app or website",
        "explanation": "Unexpected reset messages can be used to trick users into revealing credentials. Check account activity through a trusted channel.",
        "defence_tip": "Use unique passwords and enable multifactor authentication where available."
    },
    {
        "attack_type": "Credential Theft",
        "title": "Fake Public Wi-Fi Sign-In",
        "difficulty": "HARD",
        "scenario_text": "At a cafe, a public Wi-Fi login page asks for your email password instead of a normal network access code. What should you do?",
        "options": [
            "Enter your email password to get free Wi-Fi",
            "Use the same password as your banking account",
            "Avoid entering your email password and verify the network with cafe staff",
            "Disable your device's security settings"
        ],
        "correct_answer": "Avoid entering your email password and verify the network with cafe staff",
        "explanation": "A suspicious Wi-Fi portal may be attempting to collect account credentials. A network login should not require your unrelated email password.",
        "defence_tip": "Verify public networks and avoid entering sensitive credentials into unfamiliar captive portals."
    },
    {
        "attack_type": "Credential Theft",
        "title": "Password Reuse Warning",
        "difficulty": "HARD",
        "scenario_text": "You learn that a shopping website you use has suffered a data breach. You used the same password on your email account. What should you do?",
        "options": [
            "Keep using the password everywhere",
            "Change the reused password on affected accounts and enable multifactor authentication",
            "Post the password online to warn others",
            "Disable security alerts on your email"
        ],
        "correct_answer": "Change the reused password on affected accounts and enable multifactor authentication",
        "explanation": "Attackers may try exposed passwords on other services. Reusing passwords increases the risk of multiple accounts being compromised.",
        "defence_tip": "Use a different strong password for every account and consider a reputable password manager."
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
              AND LOWER(TRIM(attack_type)) = 'credential theft'
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
    print(f"\nCredential Theft setup completed! Added {added} new questions.")

    cursor.execute("""
        SELECT title, difficulty
        FROM scenarios
        WHERE LOWER(TRIM(attack_type)) = 'credential theft'
    """)

    for title, difficulty in cursor.fetchall():
        print(f"- {title} [{difficulty}]")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    conn.close()