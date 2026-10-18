import sqlite3
import json
import os

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

questions = [
    {
        "attack_type": "Malicious APK",
        "title": "Fake Video Player APK",
        "difficulty": "Easy",
        "scenario_text": "You receive a message containing an APK file that claims to be a premium video player. The app is not available on the official app store and asks for several permissions during installation.",
        "options": [
            "Install it because the video player looks useful",
            "Share the APK with friends",
            "Avoid installing it and use the official app store",
            "Disable phone security settings and install it"
        ],
        "correct_answer": "Avoid installing it and use the official app store",
        "explanation": "APK files from unknown sources can contain malicious software. Apps should be obtained from trusted official sources whenever possible.",
        "defence_tip": "Avoid installing APK files received through unexpected messages or unknown websites."
    },

    {
        "attack_type": "Malicious APK",
        "title": "Fake Mobile Update APK",
        "difficulty": "Easy",
        "scenario_text": "A website displays a warning saying your phone needs an urgent security update and provides an APK download button.",
        "options": [
            "Download and install the APK immediately",
            "Check for updates through the phone's official settings",
            "Disable Google Play Protect",
            "Give the APK accessibility permission"
        ],
        "correct_answer": "Check for updates through the phone's official settings",
        "explanation": "Legitimate mobile operating-system updates are normally delivered through the device's built-in update mechanism.",
        "defence_tip": "Use your phone's official system-update settings instead of installing update APKs from websites."
    },

    {
        "attack_type": "Malicious APK",
        "title": "Unknown Game APK",
        "difficulty": "Medium",
        "scenario_text": "A friend sends you an APK for a paid mobile game and says it is a free modified version. The APK requests access to SMS, contacts, and accessibility features.",
        "options": [
            "Install it because it is free",
            "Grant all permissions to make the game work",
            "Avoid the APK and download the game from a trusted official source",
            "Forward the APK to other friends"
        ],
        "correct_answer": "Avoid the APK and download the game from a trusted official source",
        "explanation": "Modified or unofficial APKs may contain unwanted or malicious functionality, especially when they request sensitive permissions.",
        "defence_tip": "Prefer official app stores and avoid pirated or modified APK files."
    },

    {
        "attack_type": "Malicious APK",
        "title": "APK Requesting SMS Access",
        "difficulty": "Medium",
        "scenario_text": "You install an APK from an unknown website. It asks for SMS access even though its stated purpose does not require reading messages.",
        "options": [
            "Allow the permission without checking",
            "Give it access because every app needs SMS access",
            "Stop the installation or remove the app and review its source",
            "Share your OTP with the app developer"
        ],
        "correct_answer": "Stop the installation or remove the app and review its source",
        "explanation": "Sensitive permissions should match an app's legitimate purpose. An unrelated request for SMS access is a warning sign.",
        "defence_tip": "Review permissions carefully and avoid apps requesting unnecessary sensitive access."
    },

    {
        "attack_type": "Malicious APK",
        "title": "APK With Accessibility Permission",
        "difficulty": "Hard",
        "scenario_text": "An unknown APK claims it can improve phone performance but asks for accessibility access and permission to appear over other apps.",
        "options": [
            "Grant both permissions immediately",
            "Disable the phone's security protections",
            "Avoid the application and uninstall it if already installed",
            "Enter your banking password into the application"
        ],
        "correct_answer": "Avoid the application and uninstall it if already installed",
        "explanation": "Accessibility and overlay permissions can provide powerful control over a device. Unknown applications requesting them should be treated with caution.",
        "defence_tip": "Do not grant powerful permissions to untrusted applications."
    }
]


def add_questions():
    print("\n======================================")
    print("🛡️ CYBERGUARD DATABASE UPDATE")
    print("======================================")

    print(f"\n📂 Database:")
    print(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added = 0
    skipped = 0

    for q in questions:

        # Check whether same question already exists
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

    # Count Malicious APK questions
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM scenarios
        WHERE attack_type = ?
        """,
        ("Malicious APK",)
    )

    total = cursor.fetchone()[0]

    conn.close()

    print("\n======================================")
    print("✅ DATABASE UPDATE COMPLETED")
    print("======================================")
    print(f"➕ Added: {added}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"📱 Malicious APK questions: {total}")
    print("======================================\n")


if __name__ == "__main__":
    add_questions()