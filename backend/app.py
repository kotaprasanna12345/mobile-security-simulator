from flask import Flask, jsonify, request, send_from_directory
from database import get_connection
from ai_engine import generate_scenario
from pathlib import Path
import json


# ============================================================
# CYBERGUARD FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# FRONTEND ROUTE
# ============================================================

@app.route("/frontend/<path:filename>")
def frontend(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# ============================================================
# HOME / SERVER STATUS
# ============================================================

@app.route("/")
def home():

    return jsonify({

        "message": "CyberGuard Backend is Running",

        "status": "online",

        "version": "2.1",

        "features": [
            "Scenario Simulator",
            "User Progress",
            "Dashboard",
            "AI Scenario Generator",
            "AI Attempt Tracking",
            "Advanced Analytics"
        ]

    })


# ============================================================
# GET ALL NORMAL SCENARIOS
# ============================================================

@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM scenarios
        ORDER BY scenario_id
    """)

    rows = cursor.fetchall()

    connection.close()

    scenarios = []

    for row in rows:

        scenario = dict(row)

        if scenario.get("options"):

            try:
                scenario["options"] = json.loads(
                    scenario["options"]
                )

            except Exception:
                scenario["options"] = []

        else:
            scenario["options"] = []

        scenarios.append(scenario)

    return jsonify(scenarios)


# ============================================================
# GET ONE NORMAL SCENARIO
# ============================================================

@app.route(
    "/api/scenarios/<int:scenario_id>",
    methods=["GET"]
)
def get_scenario(scenario_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM scenarios
        WHERE scenario_id = ?
    """, (scenario_id,))

    row = cursor.fetchone()

    connection.close()

    if not row:

        return jsonify({
            "error": "Scenario not found"
        }), 404

    scenario = dict(row)

    if scenario.get("options"):

        try:
            scenario["options"] = json.loads(
                scenario["options"]
            )

        except Exception:
            scenario["options"] = []

    else:
        scenario["options"] = []

    return jsonify(scenario)


# ============================================================
# CREATE / GET USER
# ============================================================

@app.route("/api/user", methods=["POST"])
def create_user():

    data = request.get_json() or {}

    username = data.get(
        "username",
        "Cyber Security Student"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (username,))

    existing = cursor.fetchone()

    if existing:

        user_id = existing["user_id"]

        cursor.execute("""
            INSERT OR IGNORE INTO progress
            (
                user_id,
                scenarios_completed,
                correct_answers,
                total_score,
                accuracy,
                level
            )
            VALUES (?, 0, 0, 0, 0, 'Security Beginner')
        """, (user_id,))

        connection.commit()
        connection.close()

        return jsonify({

            "user_id": user_id,
            "username": existing["username"]

        })

    cursor.execute("""
        INSERT INTO users
        (
            username
        )
        VALUES (?)
    """, (username,))

    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT OR IGNORE INTO progress
        (
            user_id,
            scenarios_completed,
            correct_answers,
            total_score,
            accuracy,
            level
        )
        VALUES (?, 0, 0, 0, 0, 'Security Beginner')
    """, (user_id,))

    connection.commit()
    connection.close()

    return jsonify({

        "user_id": user_id,
        "username": username

    })


# ============================================================
# SAVE NORMAL SCENARIO ATTEMPT
# ============================================================

@app.route("/api/attempt", methods=["POST"])
def save_attempt():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    scenario_id = data.get("scenario_id")

    selected_answer = data.get(
        "selected_answer",
        ""
    )

    is_correct = int(
        data.get(
            "is_correct",
            0
        )
    )

    score = int(
        data.get(
            "score",
            0
        )
    )

    if not user_id or not scenario_id:

        return jsonify({

            "success": False,

            "error":
                "user_id and scenario_id are required"

        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO attempts
        (
            user_id,
            scenario_id,
            selected_answer,
            is_correct,
            score
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        scenario_id,
        selected_answer,
        is_correct,
        score
    ))

    connection.commit()

    cursor.execute("""
        SELECT

            COUNT(DISTINCT scenario_id)
                AS scenarios_completed,

            SUM(is_correct)
                AS correct_answers,

            SUM(score)
                AS total_score,

            COUNT(*)
                AS total_attempts

        FROM attempts

        WHERE user_id = ?
    """, (user_id,))

    stats = cursor.fetchone()

    scenarios_completed = (
        stats["scenarios_completed"] or 0
    )

    correct_answers = (
        stats["correct_answers"] or 0
    )

    total_score = (
        stats["total_score"] or 0
    )

    total_attempts = (
        stats["total_attempts"] or 0
    )

    accuracy = 0

    if total_attempts > 0:

        accuracy = (
            correct_answers /
            total_attempts
        ) * 100

    level = calculate_level(
        total_score
    )

    cursor.execute("""
        INSERT OR REPLACE INTO progress
        (
            user_id,
            scenarios_completed,
            correct_answers,
            total_score,
            accuracy,
            level
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        scenarios_completed,
        correct_answers,
        total_score,
        accuracy,
        level
    ))

    connection.commit()
    connection.close()

    return jsonify({

        "success": True,

        "scenarios_completed":
            scenarios_completed,

        "correct_answers":
            correct_answers,

        "total_score":
            total_score,

        "accuracy":
            round(
                accuracy,
                2
            ),

        "level":
            level

    })


# ============================================================
# AI SCENARIO GENERATOR
# ============================================================

@app.route(
    "/api/ai/generate",
    methods=["POST"]
)
def generate_ai_scenario():

    data = request.get_json() or {}

    attack_type = data.get(
        "attack_type",
        "SMS Phishing"
    )

    difficulty = data.get(
        "difficulty",
        "Easy"
    )

    prompt = data.get(
        "prompt",
        ""
    )

    try:

        generated = generate_scenario(
            attack_type,
            difficulty
        )

        generated_content = json.dumps(
            generated
        )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ai_generated_scenarios
            (
                attack_type,
                difficulty,
                prompt,
                generated_content
            )
            VALUES (?, ?, ?, ?)
        """, (
            generated["attack_type"],
            generated["difficulty"],
            prompt,
            generated_content
        ))

        generated_id = cursor.lastrowid

        connection.commit()
        connection.close()

        generated["generated_id"] = (
            generated_id
        )

        return jsonify({

            "success": True,

            "message":
                "AI scenario generated successfully",

            "scenario":
                generated

        })

    except Exception as error:

        print(
            "AI Generation Error:",
            error
        )

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ============================================================
# SAVE AI SCENARIO ATTEMPT
# ============================================================

@app.route(
    "/api/ai/attempt",
    methods=["POST"]
)
def save_ai_attempt():

    data = request.get_json() or {}

    user_id = data.get("user_id")

    ai_scenario_id = data.get(
        "ai_scenario_id"
    )

    selected_answer = data.get(
        "selected_answer",
        ""
    )

    correct_answer = data.get(
        "correct_answer",
        ""
    )

    is_correct = int(
        data.get(
            "is_correct",
            0
        )
    )

    score = int(
        data.get(
            "score",
            0
        )
    )

    if not user_id:

        return jsonify({

            "success": False,

            "error":
                "user_id is required"

        }), 400

    if not ai_scenario_id:

        return jsonify({

            "success": False,

            "error":
                "ai_scenario_id is required"

        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "User not found"

        }), 404

    cursor.execute("""
        SELECT id
        FROM ai_generated_scenarios
        WHERE id = ?
    """, (ai_scenario_id,))

    scenario = cursor.fetchone()

    if not scenario:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "AI scenario not found"

        }), 404

    cursor.execute("""
        INSERT INTO ai_attempts
        (
            user_id,
            ai_scenario_id,
            selected_answer,
            correct_answer,
            is_correct,
            score
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        ai_scenario_id,
        selected_answer,
        correct_answer,
        is_correct,
        score
    ))

    attempt_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return jsonify({

        "success": True,

        "message":
            "AI attempt saved successfully",

        "attempt_id":
            attempt_id,

        "is_correct":
            is_correct,

        "score":
            score

    })


# ============================================================
# AI STATISTICS
# ============================================================

@app.route(
    "/api/ai/stats/<int:user_id>",
    methods=["GET"]
)
def get_ai_stats(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            COUNT(*) AS total_attempts,

            SUM(is_correct)
                AS correct_answers,

            SUM(score)
                AS total_score

        FROM ai_attempts

        WHERE user_id = ?
    """, (user_id,))

    stats = cursor.fetchone()

    total_attempts = (
        stats["total_attempts"] or 0
    )

    correct_answers = (
        stats["correct_answers"] or 0
    )

    total_score = (
        stats["total_score"] or 0
    )

    accuracy = 0

    if total_attempts > 0:

        accuracy = (
            correct_answers /
            total_attempts
        ) * 100

    connection.close()

    return jsonify({

        "total_attempts":
            total_attempts,

        "correct_answers":
            correct_answers,

        "total_score":
            total_score,

        "accuracy":
            round(
                accuracy,
                2
            )

    })


# ============================================================
# ADVANCED ANALYTICS
# ============================================================

@app.route(
    "/api/analytics/<int:user_id>",
    methods=["GET"]
)
def get_analytics(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # VERIFY USER
    # ========================================================

    cursor.execute("""
        SELECT *
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        connection.close()

        return jsonify({

            "success": False,

            "error":
                "User not found"

        }), 404

    # ========================================================
    # OVERALL ANALYTICS
    # ========================================================

    cursor.execute("""
        SELECT

            COUNT(*) AS total_attempts,

            COALESCE(SUM(is_correct), 0)
                AS correct_answers,

            COALESCE(SUM(score), 0)
                AS total_score

        FROM (

            SELECT
                is_correct,
                score

            FROM attempts

            WHERE user_id = ?

            UNION ALL

            SELECT
                is_correct,
                score

            FROM ai_attempts

            WHERE user_id = ?

        )

    """, (user_id, user_id))

    overall_row = cursor.fetchone()

    total_attempts = (
        overall_row["total_attempts"] or 0
    )

    correct_answers = (
        overall_row["correct_answers"] or 0
    )

    total_score = (
        overall_row["total_score"] or 0
    )

    accuracy = 0

    if total_attempts > 0:

        accuracy = (
            correct_answers /
            total_attempts
        ) * 100

    # ========================================================
    # NORMAL ATTACK TYPE ANALYTICS
    # ========================================================

    cursor.execute("""
        SELECT

            s.attack_type,

            COUNT(a.attempt_id)
                AS attempts,

            COALESCE(
                SUM(a.is_correct),
                0
            ) AS correct_answers,

            COALESCE(
                SUM(a.score),
                0
            ) AS score

        FROM attempts a

        JOIN scenarios s

        ON a.scenario_id =
           s.scenario_id

        WHERE a.user_id = ?

        GROUP BY s.attack_type

        ORDER BY attempts DESC

    """, (user_id,))

    normal_attack_rows = cursor.fetchall()

    attack_types = []

    for row in normal_attack_rows:

        item = dict(row)

        attempts = item["attempts"] or 0

        correct = item["correct_answers"] or 0

        item["accuracy"] = round(
            (correct / attempts) * 100,
            2
        ) if attempts > 0 else 0

        item["source"] = "normal"

        attack_types.append(item)

    # ========================================================
    # AI ATTACK TYPE ANALYTICS
    # ========================================================

    cursor.execute("""
        SELECT

            g.attack_type,

            COUNT(a.attempt_id)
                AS attempts,

            COALESCE(
                SUM(a.is_correct),
                0
            ) AS correct_answers,

            COALESCE(
                SUM(a.score),
                0
            ) AS score

        FROM ai_attempts a

        JOIN ai_generated_scenarios g

        ON a.ai_scenario_id =
           g.id

        WHERE a.user_id = ?

        GROUP BY g.attack_type

        ORDER BY attempts DESC

    """, (user_id,))

    ai_attack_rows = cursor.fetchall()

    ai_attack_types = []

    for row in ai_attack_rows:

        item = dict(row)

        attempts = item["attempts"] or 0

        correct = item["correct_answers"] or 0

        item["accuracy"] = round(
            (correct / attempts) * 100,
            2
        ) if attempts > 0 else 0

        item["source"] = "ai"

        ai_attack_types.append(item)

    # ========================================================
    # COMBINED ATTACK TYPE ANALYTICS
    # ========================================================

    combined_attack_data = {}

    for item in attack_types:

        attack = item["attack_type"]

        combined_attack_data[attack] = {

            "attack_type": attack,

            "attempts":
                item["attempts"],

            "correct_answers":
                item["correct_answers"],

            "score":
                item["score"]

        }

    for item in ai_attack_types:

        attack = item["attack_type"]

        if attack not in combined_attack_data:

            combined_attack_data[attack] = {

                "attack_type": attack,

                "attempts": 0,

                "correct_answers": 0,

                "score": 0

            }

        combined_attack_data[attack]["attempts"] += (
            item["attempts"]
        )

        combined_attack_data[attack]["correct_answers"] += (
            item["correct_answers"]
        )

        combined_attack_data[attack]["score"] += (
            item["score"]
        )

    combined_attack_types = []

    for item in combined_attack_data.values():

        attempts = item["attempts"]

        correct = item["correct_answers"]

        item["accuracy"] = round(
            (correct / attempts) * 100,
            2
        ) if attempts > 0 else 0

        combined_attack_types.append(item)

    combined_attack_types.sort(
        key=lambda x: x["attempts"],
        reverse=True
    )

    # ========================================================
    # DIFFICULTY ANALYTICS
    # ========================================================

    cursor.execute("""
        SELECT

            difficulty,

            COUNT(*) AS attempts,

            COALESCE(
                SUM(is_correct),
                0
            ) AS correct_answers,

            COALESCE(
                SUM(score),
                0
            ) AS score

        FROM (

            SELECT

                s.difficulty,

                a.is_correct,

                a.score

            FROM attempts a

            JOIN scenarios s

            ON a.scenario_id =
               s.scenario_id

            WHERE a.user_id = ?

            UNION ALL

            SELECT

                g.difficulty,

                a.is_correct,

                a.score

            FROM ai_attempts a

            JOIN ai_generated_scenarios g

            ON a.ai_scenario_id =
               g.id

            WHERE a.user_id = ?

        )

        GROUP BY difficulty

    """, (user_id, user_id))

    difficulty_rows = cursor.fetchall()

    difficulty_data = []

    difficulty_order = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3,
        "Expert": 4
    }

    for row in difficulty_rows:

        item = dict(row)

        attempts = item["attempts"] or 0

        correct = item["correct_answers"] or 0

        item["accuracy"] = round(
            (correct / attempts) * 100,
            2
        ) if attempts > 0 else 0

        difficulty_data.append(item)

    difficulty_data.sort(
        key=lambda x:
            difficulty_order.get(
                x["difficulty"],
                99
            )
    )

    # ========================================================
    # WEAK AREA
    # ========================================================

    weak_area = None

    if combined_attack_types:

        weak_area = min(
            combined_attack_types,
            key=lambda x: x["accuracy"]
        )

    # ========================================================
    # STRONG AREA
    # ========================================================

    strong_area = None

    if combined_attack_types:

        strong_area = max(
            combined_attack_types,
            key=lambda x: x["accuracy"]
        )

    connection.close()

    # ========================================================
    # FINAL ANALYTICS RESPONSE
    # ========================================================

    return jsonify({

        "success": True,

        "user": {
            "user_id":
                user["user_id"],

            "username":
                user["username"]
        },

        "overall": {

            "total_attempts":
                total_attempts,

            "correct_answers":
                correct_answers,

            "total_score":
                total_score,

            "accuracy":
                round(
                    accuracy,
                    2
                ),

            "level":
                calculate_level(
                    total_score
                )

        },

        "attack_types":
            combined_attack_types,

        "normal_attack_types":
            attack_types,

        "ai_attack_types":
            ai_attack_types,

        "difficulty":
            difficulty_data,

        "insights": {

            "weak_area":
                weak_area,

            "strong_area":
                strong_area

        }

    })


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/api/dashboard/<int:user_id>",
    methods=["GET"]
)
def dashboard(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # GET USER
    # ========================================================

    cursor.execute("""
        SELECT *
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        connection.close()

        return jsonify({

            "error":
                "User not found"

        }), 404

    # ========================================================
    # NORMAL ATTEMPTS
    # ========================================================

    cursor.execute("""
        SELECT

            COUNT(DISTINCT scenario_id)
                AS scenarios_completed,

            SUM(is_correct)
                AS correct_answers,

            SUM(score)
                AS total_score,

            COUNT(*)
                AS total_attempts

        FROM attempts

        WHERE user_id = ?

    """, (user_id,))

    normal_stats = cursor.fetchone()

    normal_completed = (
        normal_stats[
            "scenarios_completed"
        ] or 0
    )

    normal_correct = (
        normal_stats[
            "correct_answers"
        ] or 0
    )

    normal_score = (
        normal_stats[
            "total_score"
        ] or 0
    )

    normal_attempts = (
        normal_stats[
            "total_attempts"
        ] or 0
    )

    # ========================================================
    # AI ATTEMPTS
    # ========================================================

    cursor.execute("""
        SELECT

            COUNT(*) AS total_attempts,

            SUM(is_correct)
                AS correct_answers,

            SUM(score)
                AS total_score

        FROM ai_attempts

        WHERE user_id = ?

    """, (user_id,))

    ai_stats = cursor.fetchone()

    ai_attempts = (
        ai_stats[
            "total_attempts"
        ] or 0
    )

    ai_correct = (
        ai_stats[
            "correct_answers"
        ] or 0
    )

    ai_score = (
        ai_stats[
            "total_score"
        ] or 0
    )

    # ========================================================
    # COMBINED STATISTICS
    # ========================================================

    total_attempts = (
        normal_attempts +
        ai_attempts
    )

    correct_answers = (
        normal_correct +
        ai_correct
    )

    total_score = (
        normal_score +
        ai_score
    )

    scenarios_completed = (
        normal_completed
    )

    accuracy = 0

    if total_attempts > 0:

        accuracy = (
            correct_answers /
            total_attempts
        ) * 100

    level = calculate_level(
        total_score
    )

    # ========================================================
    # RECENT NORMAL ACTIVITY
    # ========================================================

    cursor.execute("""
        SELECT

            attempts.*,

            scenarios.title,

            scenarios.attack_type,

            scenarios.difficulty

        FROM attempts

        LEFT JOIN scenarios

        ON attempts.scenario_id =
           scenarios.scenario_id

        WHERE attempts.user_id = ?

        ORDER BY attempts.attempted_at DESC

        LIMIT 10

    """, (user_id,))

    normal_activity_rows = (
        cursor.fetchall()
    )

    recent_activity = []

    for row in normal_activity_rows:

        item = dict(row)

        item["source"] = "normal"

        recent_activity.append(
            item
        )

    # ========================================================
    # RECENT AI ACTIVITY
    # ========================================================

    cursor.execute("""
        SELECT

            ai_attempts.*,

            ai_generated_scenarios.attack_type,

            ai_generated_scenarios.difficulty,

            ai_generated_scenarios.generated_content

        FROM ai_attempts

        LEFT JOIN ai_generated_scenarios

        ON ai_attempts.ai_scenario_id =
           ai_generated_scenarios.id

        WHERE ai_attempts.user_id = ?

        ORDER BY ai_attempts.attempted_at DESC

        LIMIT 10

    """, (user_id,))

    ai_activity_rows = (
        cursor.fetchall()
    )

    for row in ai_activity_rows:

        item = dict(row)

        item["source"] = "ai"

        try:

            content = json.loads(
                item["generated_content"]
            )

            item["title"] = content.get(
                "title",
                "AI Generated Scenario"
            )

        except Exception:

            item["title"] = (
                "AI Generated Scenario"
            )

        item.pop(
            "generated_content",
            None
        )

        recent_activity.append(
            item
        )

    # ========================================================
    # SORT RECENT ACTIVITY
    # ========================================================

    recent_activity.sort(

        key=lambda item:
            item.get(
                "attempted_at",
                ""
            ),

        reverse=True

    )

    recent_activity = (
        recent_activity[:10]
    )

    connection.close()

    # ========================================================
    # RESPONSE
    # ========================================================

    return jsonify({

        "user":
            dict(user),

        "stats": {

            "scenarios_completed":
                scenarios_completed,

            "correct_answers":
                correct_answers,

            "total_score":
                total_score,

            "accuracy":
                round(
                    accuracy,
                    2
                ),

            "level":
                level,

            "total_attempts":
                total_attempts,

            "normal_attempts":
                normal_attempts,

            "ai_attempts":
                ai_attempts,

            "ai_correct_answers":
                ai_correct,

            "ai_score":
                ai_score

        },

        "recent_activity":
            recent_activity

    })


# ============================================================
# SECURITY LEVEL CALCULATOR
# ============================================================

def calculate_level(total_score):

    if total_score >= 50:

        return "Cyber Guardian"

    elif total_score >= 30:

        return "Security Expert"

    elif total_score >= 15:

        return "Threat Hunter"

    elif total_score >= 5:

        return "Security Defender"

    else:

        return "Security Beginner"


# ============================================================
# CORS
# ============================================================

@app.after_request
def add_cors_headers(response):

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, OPTIONS"

    return response


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()

    print("======================================")
    print("🛡️  CYBERGUARD BACKEND")
    print("======================================")

    print("🚀 Server starting...")
    print()

    print("🌐 Main:")
    print("   http://localhost:5000")
    print()

    print("🏠 Frontend:")
    print(
        "   http://localhost:5000/frontend/index.html"
    )
    print()

    print("🎮 Simulator:")
    print(
        "   http://localhost:5000/frontend/simulator.html"
    )
    print()

    print("📊 Dashboard:")
    print(
        "   http://localhost:5000/frontend/dashboard.html"
    )
    print()

    print("🤖 AI Generator:")
    print(
        "   http://localhost:5000/frontend/ai-generator.html"
    )
    print()

    print("📡 API:")
    print(
        "   http://localhost:5000/api/scenarios"
    )
    print()

    print("🤖 AI API:")
    print(
        "   http://localhost:5000/api/ai/generate"
    )
    print()

    print("🧠 AI Attempt API:")
    print(
        "   http://localhost:5000/api/ai/attempt"
    )
    print()

    print("📈 AI Stats API:")
    print(
        "   http://localhost:5000/api/ai/stats/1"
    )
    print()

    print("📊 Analytics API:")
    print(
        "   http://localhost:5000/api/analytics/1"
    )
    print()

    print("======================================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
