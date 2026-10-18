import sqlite3
import json

DB_PATH = "../data/simulator.db"

options_data = {

    1: [
        "Click the verification link immediately",
        "Reply to the SMS with your personal details",
        "Open the official telecom app or website and verify the message",
        "Share the message with friends"
    ],

    2: [
        "Click the link and enter your address",
        "Verify whether the offer exists through the company's official website",
        "Send your phone number to the sender",
        "Download the attached application"
    ],

    3: [
        "Click the link and enter your banking details",
        "Reply to the SMS with your password",
        "Use the official banking app or website to check your account",
        "Share the message on social media"
    ],

    4: [
        "Pay the delivery fee using the SMS link",
        "Enter your address on the linked website",
        "Check the delivery status through the official courier website or app",
        "Reply with your personal information"
    ],

    5: [
        "Enter the OTP into the verification link",
        "Send the OTP to the person who contacted you",
        "Open the official service app and check the account security alerts",
        "Ignore all security alerts permanently"
    ],

    6: [
        "Click the bank verification link",
        "Open the official banking app and verify the message",
        "Enter your banking password on the linked page",
        "Reply with your account details"
    ],

    7: [
        "Click the delivery link immediately",
        "Track the package using the official delivery website",
        "Pay the requested fee through the SMS",
        "Send your address to the sender"
    ],

    8: [
        "Complete KYC using the provided link",
        "Share your OTP with the sender",
        "Contact the telecom provider through its official channel",
        "Download the APK attached to the message"
    ],

    9: [
        "Share the OTP with the support representative",
        "Post the OTP online for verification",
        "Do not share the OTP and contact the official service",
        "Enter the OTP into the SMS link"
    ],

    10: [
        "Install the app because the logo looks genuine",
        "Check the official bank website or app store listing before installing",
        "Give the app all requested permissions",
        "Enter your banking credentials immediately"
    ],

    11: [
        "Install the APK from the browser",
        "Disable phone security settings",
        "Check for updates through the phone's official settings",
        "Give the APK accessibility permission"
    ],

    12: [
        "Install it because the icon looks identical",
        "Check the developer and official app listing",
        "Give it access to contacts immediately",
        "Enter your social media password"
    ],

    13: [
        "Install the payment app because it came from a QR code",
        "Give the app all requested permissions",
        "Avoid it and use a verified payment application",
        "Disable your phone's security settings"
    ],

    14: [
        "Give the app accessibility permission",
        "Install another unknown security app",
        "Uninstall the suspicious app and use a trusted security solution",
        "Ignore all phone security warnings"
    ]
}


connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

for scenario_id, options in options_data.items():

    cursor.execute(
        "UPDATE scenarios SET options = ? WHERE scenario_id = ?",
        (json.dumps(options), scenario_id)
    )

connection.commit()

print("✅ Options added successfully!")

rows = cursor.execute(
    "SELECT scenario_id, options FROM scenarios ORDER BY scenario_id"
).fetchall()

print(f"📊 Scenarios updated: {len(rows)}")

connection.close()