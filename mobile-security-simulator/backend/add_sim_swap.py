import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

questions = [
    {
        "attack_type": "SIM Swap",
        "title": "Unexpected SIM Deactivation",
        "difficulty": "Easy",
        "scenario_text": "Your phone suddenly loses mobile network connectivity, and you receive a notification that your SIM has been deactivated. You did not request any SIM replacement.",
        "options": [
            "Wait for the network to return",
            "Contact your mobile carrier through its official customer-care channel",
            "Share your OTP with anyone who contacts you",
            "Post your phone number on social media"
        ],
        "correct_answer": "Contact your mobile carrier through its official customer-care channel",
        "explanation": "Unexpected loss of mobile service can be a warning sign of unauthorized SIM replacement. The safest response is to contact the carrier through an official channel.",
        "defence_tip": "Contact your mobile carrier immediately if your SIM unexpectedly stops working."
    },

    {
        "attack_type": "SIM Swap",
        "title": "Fake Telecom Support Call",
        "difficulty": "Easy",
        "scenario_text": "Someone calls claiming to be from your mobile provider and asks for an OTP to complete a SIM upgrade.",
        "options": [
            "Give the OTP because they claim to be support staff",
            "Read the OTP slowly so they can verify it",
            "Refuse to share the OTP and contact the carrier through an official channel",
            "Send your account password instead"
        ],
        "correct_answer": "Refuse to share the OTP and contact the carrier through an official channel",
        "explanation": "OTP codes are authentication secrets and should not be shared with callers. A legitimate support process should be verified independently.",
        "defence_tip": "Never disclose OTPs to callers claiming to represent your telecom provider."
    },

    {
        "attack_type": "SIM Swap",
        "title": "Unexpected SIM Replacement Message",
        "difficulty": "Medium",
        "scenario_text": "You receive a message saying that a new SIM replacement request has been created for your phone number, but you never requested one.",
        "options": [
            "Ignore the message",
            "Click any link in the message to cancel it",
            "Contact the mobile carrier through its official app, website, or customer-care channel",
            "Forward the message to friends"
        ],
        "correct_answer": "Contact the mobile carrier through its official app, website, or customer-care channel",
        "explanation": "An unexpected SIM replacement notification can indicate unauthorized activity. Verification should be done through an official carrier channel rather than links in the message.",
        "defence_tip": "Verify unexpected SIM-related notifications directly with your telecom provider."
    },

    {
        "attack_type": "SIM Swap",
        "title": "Account Recovery After SIM Loss",
        "difficulty": "Medium",
        "scenario_text": "Your phone suddenly stops receiving calls and SMS messages while your online accounts begin showing unusual login notifications.",
        "options": [
            "Continue using your accounts normally",
            "Share your account password with a caller offering help",
            "Contact your carrier and secure affected accounts using trusted recovery methods",
            "Post the login alerts publicly"
        ],
        "correct_answer": "Contact your carrier and secure affected accounts using trusted recovery methods",
        "explanation": "Loss of mobile service combined with unusual account activity can indicate an account takeover attempt. Both the mobile number and affected accounts should be secured.",
        "defence_tip": "If you suspect a SIM-related attack, secure your mobile account and important online accounts immediately."
    },

    {
        "attack_type": "SIM Swap",
        "title": "Protecting Against SIM Swap",
        "difficulty": "Hard",
        "scenario_text": "You want to reduce the risk of someone taking control of your phone number through an unauthorized SIM replacement.",
        "options": [
            "Share your OTP whenever someone requests it",
            "Use carrier account protections and avoid sharing sensitive authentication information",
            "Keep all account information public",
            "Use the same password for every account"
        ],
        "correct_answer": "Use carrier account protections and avoid sharing sensitive authentication information",
        "explanation": "Carrier account protections and careful handling of authentication information can reduce the risk of unauthorized SIM changes.",
        "defence_tip": "Use available carrier security features and never share OTPs, PINs, or account credentials."
    }
]


def add_questions():
    print("\n======================================")
    print("🛡️ CYBERGUARD DATABASE UPDATE")
    print("======================================")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added = 0
    skipped = 0

    for q in questions:

        cursor.execute(
            """
            SELECT scenario_id
            FROM scenarios
            WHERE attack_type = ? AND title = ?
            """,
            (q["attack_type"], q["title"])
        )

        existing = cursor.fetchone()

        if existing:
            print(f"⚠️ Already exists: {q['title']}")
            skipped += 1
            continue

        cursor.execute(
            """
            INSERT INTO scenarios
            (
                attack_type,
                title,
                difficulty,
                scenario_text,
                correct_answer,
                explanation,
                defence_tip,
                options,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                q["attack_type"],
                q["title"],
                q["difficulty"],
                q["scenario_text"],
                q["correct_answer"],
                q["explanation"],
                q["defence_tip"],
                json.dumps(q["options"])
            )
        )

        added += 1
        print(f"✅ Added: {q['title']}")

    conn.commit()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM scenarios
        WHERE attack_type = ?
        """,
        ("SIM Swap",)
    )

    total = cursor.fetchone()[0]

    conn.close()

    print("\n======================================")
    print("✅ DATABASE UPDATE COMPLETED")
    print("======================================")
    print(f"➕ Added: {added}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"📱 SIM Swap questions: {total}")
    print("======================================\n")


if __name__ == "__main__":
    add_questions()