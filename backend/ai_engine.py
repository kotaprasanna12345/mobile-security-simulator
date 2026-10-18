import random


# ============================================================
# CYBERGUARD LOCAL AI SCENARIO ENGINE
# ============================================================

SCENARIO_DATABASE = {

    "SMS Phishing": {

        "Easy": [
            {
                "title": "Urgent SIM Verification",
                "scenario_text": (
                    "You receive an SMS claiming that your SIM card will "
                    "be blocked today unless you complete verification "
                    "using a link in the message."
                ),
                "options": [
                    "Open the link and complete verification.",
                    "Reply to the SMS with your personal details.",
                    "Open the official telecom app or website and verify the message.",
                    "Forward the message to a friend."
                ],
                "correct_answer": (
                    "Open the official telecom app or website and verify the message."
                ),
                "defence_tip": (
                    "Do not use links from unexpected messages. "
                    "Verify account issues through the official telecom "
                    "app, website, or customer-care channel."
                ),
                "explanation": (
                    "The message creates urgency and asks you to use an "
                    "unverified link. Urgency and suspicious links are "
                    "common SMS phishing warning signs."
                )
            }
        ],

        "Medium": [
            {
                "title": "Fake Bank Security Alert",
                "scenario_text": (
                    "An SMS claims that unusual activity was detected on "
                    "your bank account. It asks you to click a shortened "
                    "URL and confirm your account details immediately."
                ),
                "options": [
                    "Click the shortened URL and verify the account.",
                    "Ignore the link and independently open your bank's official app.",
                    "Reply with your account number to confirm ownership.",
                    "Call the phone number included in the SMS."
                ],
                "correct_answer": (
                    "Ignore the link and independently open your bank's official app."
                ),
                "defence_tip": (
                    "Access your bank through its official application "
                    "or manually typed website instead of using links "
                    "received through SMS."
                ),
                "explanation": (
                    "Attackers often use shortened links and urgent "
                    "security claims to redirect victims to "
                    "credential-stealing websites."
                )
            }
        ],

        "Hard": [
            {
                "title": "Targeted Account Recovery Scam",
                "scenario_text": (
                    "You receive an SMS mentioning your bank's name and "
                    "the last four digits of an old card. It claims that "
                    "an account recovery request is pending and provides "
                    "a link to cancel it."
                ),
                "options": [
                    "Use the link because the message contains accurate personal information.",
                    "Reply to the sender and ask how they obtained your details.",
                    "Open your bank's official app and check for security notifications.",
                    "Send the requested verification information through SMS."
                ],
                "correct_answer": (
                    "Open your bank's official app and check for security notifications."
                ),
                "defence_tip": (
                    "Treat accurate-looking personal details as insufficient "
                    "proof of authenticity. Verify suspicious account "
                    "activity using official channels."
                ),
                "explanation": (
                    "Attackers may use previously leaked information to "
                    "make phishing messages appear legitimate."
                )
            }
        ],

        "Expert": [
            {
                "title": "Multi-Stage SIM Swap Warning",
                "scenario_text": (
                    "A message claims that a SIM replacement request was "
                    "initiated from another city. It provides a customer "
                    "care number and asks you to immediately provide an "
                    "OTP to cancel the request."
                ),
                "options": [
                    "Provide the OTP because the request is urgent.",
                    "Call the number included in the message.",
                    "Use the telecom provider's official contact channel and never disclose the OTP.",
                    "Forward the OTP to customer support."
                ],
                "correct_answer": (
                    "Use the telecom provider's official contact channel and never disclose the OTP."
                ),
                "defence_tip": (
                    "Never disclose OTPs. Contact the telecom provider "
                    "through a trusted official channel when dealing "
                    "with SIM-related alerts."
                ),
                "explanation": (
                    "This combines social engineering, urgency, and OTP "
                    "theft techniques. The attacker may be attempting "
                    "to gain control of the victim's mobile number."
                )
            }
        ]
    },


    "Fake App": {

        "Easy": [
            {
                "title": "Fake Banking Application",
                "scenario_text": (
                    "You find a banking application on a third-party "
                    "website offering special rewards. The app requests "
                    "SMS, contacts, and accessibility permissions."
                ),
                "options": [
                    "Install it because it offers rewards.",
                    "Install it and disable permissions later.",
                    "Download the banking application only from the official app store or bank website.",
                    "Share the application with friends."
                ],
                "correct_answer": (
                    "Download the banking application only from the official app store or bank website."
                ),
                "defence_tip": (
                    "Install applications only from trusted official "
                    "sources and carefully review permissions."
                ),
                "explanation": (
                    "A banking application from an unofficial source "
                    "requesting excessive permissions can indicate "
                    "malicious behavior."
                )
            }
        ],

        "Medium": [
            {
                "title": "Imitation Wallet Application",
                "scenario_text": (
                    "A payment application looks almost identical to a "
                    "popular wallet app. Its developer name is unfamiliar "
                    "and it requests access to SMS messages and contacts."
                ),
                "options": [
                    "Install it because the interface looks authentic.",
                    "Check the developer, reviews, permissions, and official listing.",
                    "Give it every requested permission.",
                    "Use it only for small transactions."
                ],
                "correct_answer": (
                    "Check the developer, reviews, permissions, and official listing."
                ),
                "defence_tip": (
                    "Verify the publisher, download source, reviews, "
                    "permissions, and application identity before installation."
                ),
                "explanation": (
                    "Visual similarity does not prove authenticity. "
                    "Fake applications frequently imitate trusted brands."
                )
            }
        ],

        "Hard": [
            {
                "title": "Malicious Productivity App",
                "scenario_text": (
                    "A productivity app from an unknown developer has "
                    "thousands of downloads and positive-looking reviews. "
                    "It requests accessibility and notification access."
                ),
                "options": [
                    "Install it because it has many downloads.",
                    "Trust the reviews and enable every permission.",
                    "Investigate the developer and permissions before installing.",
                    "Disable security warnings before installing."
                ],
                "correct_answer": (
                    "Investigate the developer and permissions before installing."
                ),
                "defence_tip": (
                    "Downloads and reviews alone are not proof of safety. "
                    "Examine permissions and verify the developer."
                ),
                "explanation": (
                    "Malicious applications can abuse accessibility and "
                    "notification permissions to monitor or interact with "
                    "other applications."
                )
            }
        ],

        "Expert": [
            {
                "title": "Trojanized Security Scanner",
                "scenario_text": (
                    "A security scanner from an unofficial website claims "
                    "to detect advanced mobile threats. After installation "
                    "it requests accessibility, SMS, notification, and "
                    "device-admin permissions."
                ),
                "options": [
                    "Enable every permission because security apps need full access.",
                    "Install it temporarily and remove it later.",
                    "Do not install it and obtain security software from a trusted source.",
                    "Disable mobile security warnings."
                ],
                "correct_answer": (
                    "Do not install it and obtain security software from a trusted source."
                ),
                "defence_tip": (
                    "Security tools themselves should come from trusted "
                    "sources. Excessive privileges combined with unofficial "
                    "distribution are major warning signs."
                ),
                "explanation": (
                    "Attackers can disguise malware as security software "
                    "to gain extensive privileges on a mobile device."
                )
            }
        ]
    },


    "QR Scam": {

        "Easy": [
            {
                "title": "Suspicious QR Payment Request",
                "scenario_text": (
                    "A stranger sends you a QR code and claims that "
                    "scanning it will allow them to send money to your "
                    "account. The message asks you to approve a payment."
                ),
                "options": [
                    "Scan the QR code and approve the payment.",
                    "Scan it only if the amount is small.",
                    "Do not scan it and verify the transaction through the official payment application.",
                    "Forward the QR code to another person."
                ],
                "correct_answer": (
                    "Do not scan it and verify the transaction through the official payment application."
                ),
                "defence_tip": (
                    "Be cautious with unexpected QR codes. Verify payment "
                    "requests inside the official payment application."
                ),
                "explanation": (
                    "Attackers can use QR codes to redirect users to "
                    "malicious websites or payment pages."
                )
            }
        ],

        "Medium": [
            {
                "title": "Fake QR Verification Page",
                "scenario_text": (
                    "A poster asks you to scan a QR code to verify your "
                    "identity. The resulting page requests your username, "
                    "password, and OTP."
                ),
                "options": [
                    "Enter the credentials because the poster looks official.",
                    "Provide only the OTP.",
                    "Close the page and verify the request through the organization's official website.",
                    "Share the credentials with the poster owner."
                ],
                "correct_answer": (
                    "Close the page and verify the request through the organization's official website."
                ),
                "defence_tip": (
                    "Never enter credentials or OTPs into unexpected pages "
                    "reached through unknown QR codes."
                ),
                "explanation": (
                    "QR codes can hide the destination URL and may redirect "
                    "victims to phishing websites."
                )
            }
        ]
    },


    "OTP Scam": {

        "Easy": [
            {
                "title": "Customer Care OTP Request",
                "scenario_text": (
                    "Someone claiming to be customer support calls you and "
                    "says they need the OTP sent to your phone to verify "
                    "your identity."
                ),
                "options": [
                    "Share the OTP because they are customer support.",
                    "Share only the first few digits.",
                    "Never share the OTP and contact the organization through its official channel.",
                    "Ask them to send another OTP."
                ],
                "correct_answer": (
                    "Never share the OTP and contact the organization through its official channel."
                ),
                "defence_tip": (
                    "Never disclose OTPs to callers, messages, or unknown individuals."
                ),
                "explanation": (
                    "Attackers may impersonate customer support to obtain "
                    "one-time passwords and access accounts."
                )
            }
        ],

        "Medium": [
            {
                "title": "Urgent Account Verification Call",
                "scenario_text": (
                    "A caller claims your account will be permanently "
                    "locked unless you provide an OTP within two minutes."
                ),
                "options": [
                    "Provide the OTP immediately.",
                    "Ask the caller for their personal identification.",
                    "End the call and independently contact the organization.",
                    "Send the OTP through a messaging application."
                ],
                "correct_answer": (
                    "End the call and independently contact the organization."
                ),
                "defence_tip": (
                    "Urgency is a common social engineering technique. "
                    "End suspicious calls and use trusted contact information."
                ),
                "explanation": (
                    "The attacker is creating time pressure so the victim "
                    "makes a decision without verification."
                )
            }
        ]
    },


    "Social Engineering": {

        "Easy": [
            {
                "title": "Impersonation Request",
                "scenario_text": (
                    "Someone contacts you pretending to be a senior employee "
                    "and urgently asks you to share a confidential document."
                ),
                "options": [
                    "Send the document immediately.",
                    "Verify the person's identity through an independent channel.",
                    "Forward the request to everyone.",
                    "Share only part of the document."
                ],
                "correct_answer": (
                    "Verify the person's identity through an independent channel."
                ),
                "defence_tip": (
                    "Verify unusual requests independently, especially when "
                    "they involve confidential information or urgency."
                ),
                "explanation": (
                    "Attackers can impersonate trusted people to manipulate "
                    "victims into revealing sensitive information."
                )
            }
        ]
    },


    "Malware": {

        "Easy": [
            {
                "title": "Suspicious Security Update",
                "scenario_text": (
                    "A website displays a warning claiming your phone is "
                    "infected and asks you to download a security APK immediately."
                ),
                "options": [
                    "Download the APK immediately.",
                    "Install it after disabling browser protection.",
                    "Close the page and use trusted security tools from official sources.",
                    "Share the APK with friends."
                ],
                "correct_answer": (
                    "Close the page and use trusted security tools from official sources."
                ),
                "defence_tip": (
                    "Do not install applications prompted by suspicious "
                    "websites. Use trusted security software from official sources."
                ),
                "explanation": (
                    "Fake infection warnings are commonly used to trick "
                    "users into installing malicious software."
                )
            }
        ]
    },


    "Account Security": {

        "Easy": [
            {
                "title": "Unexpected Login Alert",
                "scenario_text": (
                    "You receive a notification that your account was "
                    "accessed from an unfamiliar location. You did not "
                    "perform the login."
                ),
                "options": [
                    "Ignore the notification.",
                    "Share your password with a friend.",
                    "Change your password and review account security activity through the official service.",
                    "Click any link in the notification."
                ],
                "correct_answer": (
                    "Change your password and review account security activity through the official service."
                ),
                "defence_tip": (
                    "Use the official account security page to review sessions, "
                    "change passwords, and enable multi-factor authentication."
                ),
                "explanation": (
                    "Unexpected login alerts can indicate compromised "
                    "credentials or unauthorized access."
                )
            }
        ]
    },


    "Password Attack": {

        "Easy": [
            {
                "title": "Repeated Login Attempts",
                "scenario_text": (
                    "Your account shows several failed login attempts "
                    "from unfamiliar locations."
                ),
                "options": [
                    "Continue using the same password.",
                    "Use the same password on another account.",
                    "Change the password to a strong unique one and enable multi-factor authentication.",
                    "Post the login alert publicly."
                ],
                "correct_answer": (
                    "Change the password to a strong unique one and enable multi-factor authentication."
                ),
                "defence_tip": (
                    "Use unique strong passwords and enable multi-factor "
                    "authentication wherever possible."
                ),
                "explanation": (
                    "Repeated failed attempts can indicate password guessing, "
                    "credential stuffing, or another unauthorized access attempt."
                )
            }
        ]
    }
}


def generate_scenario(attack_type, difficulty):
    """
    Generate a cybersecurity scenario based on
    attack type and difficulty.
    """

    if attack_type not in SCENARIO_DATABASE:
        attack_type = "SMS Phishing"

    if difficulty not in SCENARIO_DATABASE[attack_type]:
        difficulty = "Easy"

    scenarios = SCENARIO_DATABASE[attack_type][difficulty]

    scenario = random.choice(scenarios)

    generated = {
        "attack_type": attack_type,
        "difficulty": difficulty,
        "title": scenario["title"],
        "scenario_text": scenario["scenario_text"],
        "options": scenario["options"],
        "correct_answer": scenario["correct_answer"],
        "defence_tip": scenario["defence_tip"],
        "explanation": scenario["explanation"]
    }

    return generated