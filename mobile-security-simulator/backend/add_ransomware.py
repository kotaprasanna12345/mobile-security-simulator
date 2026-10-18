
import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "simulator.db")

scenarios = [
    {
        "attack_type": "Ransomware",
        "title": "Files Suddenly Encrypted",
        "difficulty": "HARD",
        "scenario_text": "Your phone suddenly displays a message saying your files are encrypted and you must pay money to recover them. What should you do first?",
        "options": [
            "Pay immediately without checking anything",
            "Disconnect the device from networks and seek trusted security assistance",
            "Enter your banking password into the message",
            "Forward the message to all your contacts"
        ],
        "correct_answer": "Disconnect the device from networks and seek trusted security assistance",
        "explanation": "Ransomware may encrypt files and demand payment. Isolating the device can help limit further network activity while you seek trusted help.",
        "defence_tip": "Keep important files backed up and never rely on paying a ransom to recover them."
    },
    {
        "attack_type": "Ransomware",
        "title": "Suspicious File Recovery App",
        "difficulty": "HARD",
        "scenario_text": "An unknown app claims it can recover your locked files if you grant it Accessibility and administrator permissions. What is the safest response?",
        "options": [
            "Grant every permission immediately",
            "Disable your phone's security protections",
            "Verify the app through a trusted security professional before taking action",
            "Share your passwords with the app developer"
        ],
        "correct_answer": "Verify the app through a trusted security professional before taking action",
        "explanation": "A fake recovery app may cause further harm or steal information. Avoid granting powerful permissions to untrusted apps.",
        "defence_tip": "Use reputable recovery tools and trusted technical support."
    },
    {
        "attack_type": "Ransomware",
        "title": "Ransom Payment Deadline",
        "difficulty": "HARD",
        "scenario_text": "A ransom note says your files will be permanently deleted in 30 minutes unless you pay. What should you do?",
        "options": [
            "Panic and pay using the first payment link",
            "Contact trusted security support and preserve the ransom note as evidence",
            "Give the attacker your email password",
            "Install another unknown app recommended in the note"
        ],
        "correct_answer": "Contact trusted security support and preserve the ransom note as evidence",
        "explanation": "Attackers may use urgent deadlines to pressure victims. Payment does not guarantee that files will be restored.",
        "defence_tip": "Do not rush into payment. Preserve evidence and seek trusted incident-response assistance."
    },
    {
        "attack_type": "Ransomware",
        "title": "Suspicious APK Attachment",
        "difficulty": "HARD",
        "scenario_text": "You receive an unexpected APK file claiming to be a document viewer. After installing it, the phone begins behaving strangely. What should you do?",
        "options": [
            "Install more files from the same sender",
            "Grant the app access to all your files",
            "Disconnect from networks if an attack is suspected and seek trusted security help",
            "Disable all security updates permanently"
        ],
        "correct_answer": "Disconnect from networks if an attack is suspected and seek trusted security help",
        "explanation": "Unexpected APK files can contain malware. Isolating a suspected compromised device can help limit further communication with attackers.",
        "defence_tip": "Avoid unexpected APK attachments and install apps only from trusted sources."
    },
    {
        "attack_type": "Ransomware",
        "title": "Recovering Files Safely",
        "difficulty": "HARD",
        "scenario_text": "Your device has been cleaned after a ransomware incident. You have a backup created before the attack. What is the safest recovery approach?",
        "options": [
            "Restore the backup after confirming the device is secure",
            "Restore files from any unknown website",
            "Disable security software before restoring files",
            "Open every suspicious file to test it"
        ],
        "correct_answer": "Restore the backup after confirming the device is secure",
        "explanation": "A clean, verified backup can help restore files without relying on the attacker. Make sure the device is secure before restoring data.",
        "defence_tip": "Maintain regular backups and test that important files can be restored."
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
              AND LOWER(TRIM(attack_type)) = 'ransomware'
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
    print(f"\nRansomware setup completed! Added {added} new questions.")

    cursor.execute("""
        SELECT title, difficulty
        FROM scenarios
        WHERE LOWER(TRIM(attack_type)) = 'ransomware'
    """)

    for title, difficulty in cursor.fetchall():
        print(f"- {title} [{difficulty}]")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    conn.close()