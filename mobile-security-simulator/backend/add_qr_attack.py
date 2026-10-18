import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

questions = [
    {
        "attack_type": "QR Code Attack",
        "title": "Suspicious Payment QR Code",
        "difficulty": "Easy",
        "scenario_text": "A stranger sends you a QR code and says scanning it will help you receive a payment. You are not sure where the QR code came from.",
        "options": [
            "Scan it immediately",
            "Verify the payment request through the official payment app before proceeding",
            "Share your UPI PIN after scanning",
            "Forward the QR code to friends"
        ],
        "correct_answer": "Verify the payment request through the official payment app before proceeding",
        "explanation": "QR codes can redirect users to unexpected websites or payment actions. A QR code should not automatically be trusted just because it looks legitimate.",
        "defence_tip": "Verify unexpected QR codes and payment requests before scanning or approving anything."
    },

    {
        "attack_type": "QR Code Attack",
        "title": "Fake Restaurant QR Code",
        "difficulty": "Easy",
        "scenario_text": "At a restaurant, you notice a QR code sticker placed over the original menu QR code. It redirects to an unfamiliar website.",
        "options": [
            "Enter your card details on the unfamiliar website",
            "Continue because it is inside the restaurant",
            "Ask the restaurant staff to verify the QR code",
            "Download any application requested by the website"
        ],
        "correct_answer": "Ask the restaurant staff to verify the QR code",
        "explanation": "Tampered QR codes can redirect users to fraudulent websites or unwanted downloads.",
        "defence_tip": "Be cautious of QR stickers that appear altered or placed over an original code."
    },

    {
        "attack_type": "QR Code Attack",
        "title": "QR Code Login Page",
        "difficulty": "Medium",
        "scenario_text": "You scan a QR code received through a message. It opens a login page asking for your email password.",
        "options": [
            "Enter your password immediately",
            "Use your banking password instead",
            "Close the page and access the service through its official app or website",
            "Share the login page with friends"
        ],
        "correct_answer": "Close the page and access the service through its official app or website",
        "explanation": "A QR code can hide the destination URL. An unexpected login page requesting credentials should be treated cautiously.",
        "defence_tip": "Use official apps or manually enter trusted website addresses instead of logging in through unexpected QR links."
    },

    {
        "attack_type": "QR Code Attack",
        "title": "QR Code App Download",
        "difficulty": "Medium",
        "scenario_text": "A QR code on a poster asks you to download an APK to claim a special offer. The download is hosted on an unfamiliar website.",
        "options": [
            "Download and install the APK",
            "Disable phone security before installing it",
            "Avoid the download and verify the offer through the official company website",
            "Give the downloaded app all permissions"
        ],
        "correct_answer": "Avoid the download and verify the offer through the official company website",
        "explanation": "QR codes can be used to direct users to untrusted downloads. APK files from unknown websites may contain malicious software.",
        "defence_tip": "Never install unknown APK files simply because a QR code directs you to them."
    },

    {
        "attack_type": "QR Code Attack",
        "title": "QR Code Payment Request",
        "difficulty": "Hard",
        "scenario_text": "You are told that scanning a QR code will allow you to receive money. After scanning, your payment app displays a request asking you to approve a payment.",
        "options": [
            "Approve the payment because you were promised money",
            "Enter your UPI PIN to receive the money",
            "Cancel the request and verify the transaction independently",
            "Send the QR code to another person"
        ],
        "correct_answer": "Cancel the request and verify the transaction independently",
        "explanation": "Receiving money normally does not require approving an unexpected payment request. Users should carefully review payment details before authorizing transactions.",
        "defence_tip": "Never approve an unexpected payment request or enter your UPI PIN simply to receive money."
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
        ("QR Code Attack",)
    )

    total = cursor.fetchone()[0]

    conn.close()

    print("\n======================================")
    print("✅ DATABASE UPDATE COMPLETED")
    print("======================================")
    print(f"➕ Added: {added}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"📱 QR Code Attack questions: {total}")
    print("======================================\n")


if __name__ == "__main__":
    add_questions()