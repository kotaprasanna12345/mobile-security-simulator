
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

scenarios = [
    {
        "attack_type": "Spyware",
        "title": "Suspicious Monitoring App",
        "difficulty": "HARD",
        "scenario_text": "You installed a flashlight app, but it requests access to your microphone, contacts, SMS, and location without a clear reason. What should you do?",
        "options": [
            "Grant all permissions so the app works properly",
            "Ignore the permissions and continue using the app",
            "Review permissions, revoke unnecessary access, and uninstall the suspicious app",
            "Share the app with friends to check whether it works"
        ],
        "correct_answer": "Review permissions, revoke unnecessary access, and uninstall the suspicious app",
        "explanation": "An app requesting unrelated sensitive permissions may be suspicious. Review its permissions and remove it if you cannot trust its purpose.",
        "defence_tip": "Install apps from trusted sources and grant only necessary permissions."
    },
    {
        "attack_type": "Spyware",
        "title": "Unknown App Running in Background",
        "difficulty": "HARD",
        "scenario_text": "Your phone battery drains unusually fast, and an unfamiliar app is using significant background data. What is the safest first step?",
        "options": [
            "Check the app's permissions, battery usage, and mobile data usage",
            "Give the app administrator access",
            "Disable all phone security settings",
            "Enter your banking password into the app"
        ],
        "correct_answer": "Check the app's permissions, battery usage, and mobile data usage",
        "explanation": "Unexpected battery or data usage can have several causes, including suspicious apps. Investigate the app before deciding what action to take.",
        "defence_tip": "Regularly review installed apps, permissions, battery usage, and data usage."
    },
    {
        "attack_type": "Spyware",
        "title": "Unexpected Accessibility Access",
        "difficulty": "HARD",
        "scenario_text": "An unknown app asks you to enable Accessibility access and says it needs this permission to provide a wallpaper. What should you do?",
        "options": [
            "Enable the permission immediately",
            "Check the app's legitimacy and deny unnecessary access",
            "Disable your phone's screen lock",
            "Allow the app to control every setting"
        ],
        "correct_answer": "Check the app's legitimacy and deny unnecessary access",
        "explanation": "Accessibility access can allow powerful interactions with a device. An unrelated wallpaper app generally should not need it.",
        "defence_tip": "Give Accessibility access only to trusted apps that genuinely need it."
    },
    {
        "attack_type": "Spyware",
        "title": "Suspicious App Installation",
        "difficulty": "HARD",
        "scenario_text": "A website asks you to install an unknown APK to claim a prize. After installation, the app requests access to messages and contacts. What should you do?",
        "options": [
            "Allow every permission to claim the prize",
            "Forward the APK to your contacts",
            "Keep the app installed but ignore its alerts",
            "Avoid granting access, uninstall the app, and run a trusted security check"
        ],
        "correct_answer": "Avoid granting access, uninstall the app, and run a trusted security check",
        "explanation": "Unknown APKs can contain harmful code. Unnecessary access to messages and contacts can expose personal information.",
        "defence_tip": "Avoid installing APK files from unknown websites and never grant unnecessary permissions."
    },
    {
        "attack_type": "Spyware",
        "title": "Possible Microphone Surveillance",
        "difficulty": "HARD",
        "scenario_text": "Your phone shows the microphone indicator when you are not intentionally recording or making a call. What should you do?",
        "options": [
            "Ignore the indicator permanently",
            "Disable all operating system updates",
            "Check which app is accessing the microphone and revoke access if suspicious",
            "Give microphone access to every installed app"
        ],
        "correct_answer": "Check which app is accessing the microphone and revoke access if suspicious",
        "explanation": "The microphone indicator helps identify apps accessing the microphone. Check recent access and investigate unfamiliar apps.",
        "defence_tip": "Review your privacy dashboard and microphone permissions regularly."
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
              AND LOWER(TRIM(attack_type)) = 'spyware'
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

    print(f"\nSpyware setup completed! Added {added} new questions.")

    cursor.execute("""
        SELECT title, difficulty
        FROM scenarios
        WHERE LOWER(TRIM(attack_type)) = 'spyware'
    """)

    for title, difficulty in cursor.fetchall():
        print(f"- {title} [{difficulty}]")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    conn.close()