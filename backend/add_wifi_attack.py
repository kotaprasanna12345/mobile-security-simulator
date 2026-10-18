import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

questions = [
    {
        "attack_type": "Wi-Fi Attack",
        "title": "Suspicious Public Wi-Fi",
        "difficulty": "Easy",
        "scenario_text": "You are at a cafe and see a free Wi-Fi network with a name similar to the cafe's official network. You are not sure which network is legitimate.",
        "options": [
            "Connect immediately because the network is free",
            "Ask the cafe staff to confirm the official Wi-Fi network",
            "Use the network for banking transactions",
            "Share your password after connecting"
        ],
        "correct_answer": "Ask the cafe staff to confirm the official Wi-Fi network",
        "explanation": "Attackers can create Wi-Fi networks with names similar to legitimate networks to trick users into connecting.",
        "defence_tip": "Verify public Wi-Fi network names with the venue before connecting."
    },
    {
        "attack_type": "Wi-Fi Attack",
        "title": "Banking on Public Wi-Fi",
        "difficulty": "Easy",
        "scenario_text": "You are connected to free public Wi-Fi at an airport and need to access your banking account.",
        "options": [
            "Access banking immediately",
            "Share your banking password over the network",
            "Use mobile data or a trusted secure connection for banking",
            "Turn off all security settings"
        ],
        "correct_answer": "Use mobile data or a trusted secure connection for banking",
        "explanation": "Public networks may not provide the same level of trust as a private network. Sensitive activities should preferably use a trusted connection.",
        "defence_tip": "Avoid sensitive transactions on untrusted public Wi-Fi."
    },
    {
        "attack_type": "Wi-Fi Attack",
        "title": "Unexpected Wi-Fi Login Page",
        "difficulty": "Medium",
        "scenario_text": "After connecting to public Wi-Fi, a login page asks you to enter your email password before allowing internet access.",
        "options": [
            "Enter your email password immediately",
            "Use your banking password instead",
            "Avoid entering sensitive passwords and verify the network with the venue",
            "Share the password with other users"
        ],
        "correct_answer": "Avoid entering sensitive passwords and verify the network with the venue",
        "explanation": "Unexpected login pages can be used to collect credentials. Users should verify that the network and login portal are legitimate.",
        "defence_tip": "Never enter important account passwords into an unfamiliar Wi-Fi login page."
    },
    {
        "attack_type": "Wi-Fi Attack",
        "title": "File Sharing on Public Wi-Fi",
        "difficulty": "Medium",
        "scenario_text": "You connect your laptop to public Wi-Fi and notice that file sharing is enabled on your device.",
        "options": [
            "Keep file sharing enabled",
            "Share your personal folders with everyone",
            "Disable unnecessary file sharing and network discovery",
            "Give other users access to your files"
        ],
        "correct_answer": "Disable unnecessary file sharing and network discovery",
        "explanation": "Unnecessary network-sharing features can expose files or services to other devices on the same network.",
        "defence_tip": "Disable unnecessary sharing and network discovery when using public networks."
    },
    {
        "attack_type": "Wi-Fi Attack",
        "title": "Sensitive Activity on Unknown Network",
        "difficulty": "Hard",
        "scenario_text": "Your phone automatically connects to an unfamiliar Wi-Fi network that you have used before. You are about to enter sensitive account information.",
        "options": [
            "Continue because the phone connected automatically",
            "Verify the network and switch to a trusted connection before entering sensitive information",
            "Disable the phone lock",
            "Share your OTP over the network"
        ],
        "correct_answer": "Verify the network and switch to a trusted connection before entering sensitive information",
        "explanation": "Automatic connections can expose users to networks they did not intend to use. Sensitive activities should be performed only after verifying the connection.",
        "defence_tip": "Turn off automatic connection to unknown networks and use trusted connections for sensitive activities."
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
        ("Wi-Fi Attack",)
    )

    total = cursor.fetchone()[0]

    conn.close()

    print("\n======================================")
    print("✅ DATABASE UPDATE COMPLETED")
    print("======================================")
    print(f"➕ Added: {added}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"📶 Wi-Fi Attack questions: {total}")
    print("======================================\n")


if __name__ == "__main__":
    add_questions()