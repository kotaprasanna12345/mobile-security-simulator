
import os
import json
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory
)

from database import get_connection
from ai_engine import generate_scenario


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
# FRONTEND CONFIGURATION
# ============================================================

app.template_folder = str(FRONTEND_DIR)
app.static_folder = str(FRONTEND_DIR)


# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template("command-center.html")


@app.route("/command-center")
def command_center():
    return render_template("command-center.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/ai-generator")
def ai_generator():
    return render_template("ai-generator.html")


@app.route("/attack-radar")
def attack_radar():
    return render_template("attack-radar.html")


@app.route("/frontend/<path:filename>")
def frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ============================================================
# HOME / SERVER STATUS
# ============================================================

@app.route("/api/status")
def api_status():
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
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM scenarios
            ORDER BY scenario_id
        """)

        rows = cursor.fetchall()
        scenarios = []

        for row in rows:
            scenario = dict(row)

            if scenario.get("options"):
                try:
                    scenario["options"] = json.loads(
                        scenario["options"]
                    )
                except (json.JSONDecodeError, TypeError):
                    scenario["options"] = []
            else:
                scenario["options"] = []

            scenarios.append(scenario)

        return jsonify(scenarios)

    except Exception as error:
        app.logger.exception("Error fetching scenarios")
        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if connection is not None:
            connection.close()


# ============================================================
# GET ONE NORMAL SCENARIO
# ============================================================

@app.route("/api/scenarios/<int:scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM scenarios
            WHERE scenario_id = ?
        """, (scenario_id,))

        row = cursor.fetchone()

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
            except (json.JSONDecodeError, TypeError):
                scenario["options"] = []
        else:
            scenario["options"] = []

        return jsonify(scenario)

    except Exception as error:
        app.logger.exception("Error fetching scenario")
        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if connection is not None:
            connection.close()


# ============================================================
# CREATE / GET USER
# ============================================================

@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}

    username = data.get(
        "username",
        "Cyber Security Student"
    )

    connection = get_connection()

    try:
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

            return jsonify({
                "user_id": user_id,
                "username": existing["username"]
            })

        cursor.execute("""
            INSERT INTO users (username)
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

        return jsonify({
            "user_id": user_id,
            "username": username
        })

    except Exception as error:
        app.logger.exception("Error creating user")
        return jsonify({
            "error": str(error)
        }), 500

    finally:
        connection.close()


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
# SAVE NORMAL SCENARIO ATTEMPT
# ============================================================

@app.route("/api/attempt", methods=["POST"])
def save_attempt():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    scenario_id = data.get("scenario_id")
    selected_answer = data.get("selected_answer", "")

    try:
        is_correct = int(data.get("is_correct", 0))
        score = int(data.get("score", 0))
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "is_correct and score must be numbers"
        }), 400

    if not user_id or not scenario_id:
        return jsonify({
            "success": False,
            "error": "user_id and scenario_id are required"
        }), 400

    connection = get_connection()

    try:
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

        cursor.execute("""
            SELECT
                COUNT(DISTINCT scenario_id) AS scenarios_completed,
                SUM(is_correct) AS correct_answers,
                SUM(score) AS total_score,
                COUNT(*) AS total_attempts
            FROM attempts
            WHERE user_id = ?
        """, (user_id,))

        stats = cursor.fetchone()

        scenarios_completed = stats["scenarios_completed"] or 0
        correct_answers = stats["correct_answers"] or 0
        total_score = stats["total_score"] or 0
        total_attempts = stats["total_attempts"] or 0

        accuracy = (
            correct_answers / total_attempts * 100
            if total_attempts else 0
        )

        level = calculate_level(total_score)

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

        return jsonify({
            "success": True,
            "scenarios_completed": scenarios_completed,
            "correct_answers": correct_answers,
            "total_score": total_score,
            "accuracy": round(accuracy, 2),
            "level": level
        })

    except Exception as error:
        connection.rollback()
        app.logger.exception("Error saving attempt")
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        connection.close()


# ============================================================
# AI SCENARIO GENERATOR
# ============================================================

@app.route("/api/ai/generate", methods=["POST"])
def generate_ai_scenario():
    data = request.get_json(silent=True) or {}

    attack_type = data.get("attack_type", "SMS Phishing")
    difficulty = data.get("difficulty", "Easy")
    prompt = data.get("prompt", "")

    connection = None

    try:
        generated = generate_scenario(
            attack_type,
            difficulty
        )

        generated_content = json.dumps(generated)

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

        generated["generated_id"] = generated_id

        return jsonify({
            "success": True,
            "message": "AI scenario generated successfully",
            "scenario": generated
        })

    except Exception as error:
        app.logger.exception("AI generation failed")
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        if connection is not None:
            connection.close()


# ============================================================
# SAVE AI SCENARIO ATTEMPT
# ============================================================

@app.route("/api/ai/attempt", methods=["POST"])
def save_ai_attempt():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    ai_scenario_id = data.get("ai_scenario_id")
    selected_answer = data.get("selected_answer", "")
    correct_answer = data.get("correct_answer", "")

    try:
        is_correct = int(data.get("is_correct", 0))
        score = int(data.get("score", 0))
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "is_correct and score must be numbers"
        }), 400

    if not user_id or not ai_scenario_id:
        return jsonify({
            "success": False,
            "error": "user_id and ai_scenario_id are required"
        }), 400

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT user_id FROM users WHERE user_id = ?
        """, (user_id,))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        cursor.execute("""
            SELECT id
            FROM ai_generated_scenarios
            WHERE id = ?
        """, (ai_scenario_id,))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "error": "AI scenario not found"
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

        return jsonify({
            "success": True,
            "message": "AI attempt saved successfully",
            "attempt_id": attempt_id,
            "is_correct": is_correct,
            "score": score
        })

    except Exception as error:
        connection.rollback()
        app.logger.exception("Error saving AI attempt")
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        connection.close()


# ============================================================
# AI STATISTICS
# ============================================================

@app.route("/api/ai/stats/<int:user_id>", methods=["GET"])
def get_ai_stats(user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_attempts,
                SUM(is_correct) AS correct_answers,
                SUM(score) AS total_score
            FROM ai_attempts
            WHERE user_id = ?
        """, (user_id,))

        stats = cursor.fetchone()

        total_attempts = stats["total_attempts"] or 0
        correct_answers = stats["correct_answers"] or 0
        total_score = stats["total_score"] or 0

        accuracy = (
            correct_answers / total_attempts * 100
            if total_attempts else 0
        )

        return jsonify({
            "total_attempts": total_attempts,
            "correct_answers": correct_answers,
            "total_score": total_score,
            "accuracy": round(accuracy, 2)
        })

    finally:
        connection.close()


# ============================================================
# ADVANCED ANALYTICS
# ============================================================

@app.route("/api/analytics/<int:user_id>", methods=["GET"])
def get_analytics(user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        cursor.execute("""
            SELECT
                COUNT(*) AS total_attempts,
                COALESCE(SUM(is_correct), 0) AS correct_answers,
                COALESCE(SUM(score), 0) AS total_score
            FROM (
                SELECT is_correct, score
                FROM attempts
                WHERE user_id = ?

                UNION ALL

                SELECT is_correct, score
                FROM ai_attempts
                WHERE user_id = ?
            )
        """, (user_id, user_id))

        overall = cursor.fetchone()

        total_attempts = overall["total_attempts"] or 0
        correct_answers = overall["correct_answers"] or 0
        total_score = overall["total_score"] or 0

        accuracy = (
            correct_answers / total_attempts * 100
            if total_attempts else 0
        )

        cursor.execute("""
            SELECT
                s.attack_type,
                COUNT(a.attempt_id) AS attempts,
                COALESCE(SUM(a.is_correct), 0) AS correct_answers,
                COALESCE(SUM(a.score), 0) AS score
            FROM attempts a
            JOIN scenarios s
                ON a.scenario_id = s.scenario_id
            WHERE a.user_id = ?
            GROUP BY s.attack_type
            ORDER BY attempts DESC
        """, (user_id,))

        normal_attack_types = []

        for row in cursor.fetchall():
            item = dict(row)
            attempts = item["attempts"] or 0
            correct = item["correct_answers"] or 0

            item["accuracy"] = round(
                correct / attempts * 100, 2
            ) if attempts else 0

            item["source"] = "normal"
            normal_attack_types.append(item)

        cursor.execute("""
            SELECT
                g.attack_type,
                COUNT(a.attempt_id) AS attempts,
                COALESCE(SUM(a.is_correct), 0) AS correct_answers,
                COALESCE(SUM(a.score), 0) AS score
            FROM ai_attempts a
            JOIN ai_generated_scenarios g
                ON a.ai_scenario_id = g.id
            WHERE a.user_id = ?
            GROUP BY g.attack_type
            ORDER BY attempts DESC
        """, (user_id,))

        ai_attack_types = []

        for row in cursor.fetchall():
            item = dict(row)
            attempts = item["attempts"] or 0
            correct = item["correct_answers"] or 0

            item["accuracy"] = round(
                correct / attempts * 100, 2
            ) if attempts else 0

            item["source"] = "ai"
            ai_attack_types.append(item)

        combined = {}

        for item in normal_attack_types:
            attack = item["attack_type"]

            combined[attack] = {
                "attack_type": attack,
                "attempts": item["attempts"],
                "correct_answers": item["correct_answers"],
                "score": item["score"]
            }

        for item in ai_attack_types:
            attack = item["attack_type"]

            if attack not in combined:
                combined[attack] = {
                    "attack_type": attack,
                    "attempts": 0,
                    "correct_answers": 0,
                    "score": 0
                }

            combined[attack]["attempts"] += item["attempts"]
            combined[attack]["correct_answers"] += item["correct_answers"]
            combined[attack]["score"] += item["score"]

        combined_attack_types = []

        for item in combined.values():
            attempts = item["attempts"]
            correct = item["correct_answers"]

            item["accuracy"] = round(
                correct / attempts * 100, 2
            ) if attempts else 0

            combined_attack_types.append(item)

        combined_attack_types.sort(
            key=lambda item: item["attempts"],
            reverse=True
        )

        cursor.execute("""
            SELECT difficulty, COUNT(*) AS attempts,
                   COALESCE(SUM(is_correct), 0) AS correct_answers,
                   COALESCE(SUM(score), 0) AS score
            FROM (
                SELECT s.difficulty, a.is_correct, a.score
                FROM attempts a
                JOIN scenarios s
                    ON a.scenario_id = s.scenario_id
                WHERE a.user_id = ?

                UNION ALL

                SELECT g.difficulty, a.is_correct, a.score
                FROM ai_attempts a
                JOIN ai_generated_scenarios g
                    ON a.ai_scenario_id = g.id
                WHERE a.user_id = ?
            )
            GROUP BY difficulty
        """, (user_id, user_id))

        difficulty_data = []

        difficulty_order = {
            "Easy": 1,
            "Medium": 2,
            "Hard": 3,
            "Expert": 4
        }

        for row in cursor.fetchall():
            item = dict(row)
            attempts = item["attempts"] or 0
            correct = item["correct_answers"] or 0

            item["accuracy"] = round(
                correct / attempts * 100, 2
            ) if attempts else 0

            difficulty_data.append(item)

        difficulty_data.sort(
            key=lambda item: difficulty_order.get(
                item["difficulty"], 99
            )
        )

        weak_area = (
            min(combined_attack_types, key=lambda x: x["accuracy"])
            if combined_attack_types else None
        )

        strong_area = (
            max(combined_attack_types, key=lambda x: x["accuracy"])
            if combined_attack_types else None
        )

        return jsonify({
            "success": True,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"]
            },
            "overall": {
                "total_attempts": total_attempts,
                "correct_answers": correct_answers,
                "total_score": total_score,
                "accuracy": round(accuracy, 2),
                "level": calculate_level(total_score)
            },
            "attack_types": combined_attack_types,
            "normal_attack_types": normal_attack_types,
            "ai_attack_types": ai_attack_types,
            "difficulty": difficulty_data,
            "insights": {
                "weak_area": weak_area,
                "strong_area": strong_area
            }
        })

    finally:
        connection.close()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/api/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        cursor.execute("""
            SELECT
                COUNT(DISTINCT scenario_id) AS scenarios_completed,
                SUM(is_correct) AS correct_answers,
                SUM(score) AS total_score,
                COUNT(*) AS total_attempts
            FROM attempts
            WHERE user_id = ?
        """, (user_id,))

        normal_stats = cursor.fetchone()

        normal_completed = normal_stats["scenarios_completed"] or 0
        normal_correct = normal_stats["correct_answers"] or 0
        normal_score = normal_stats["total_score"] or 0
        normal_attempts = normal_stats["total_attempts"] or 0

        cursor.execute("""
            SELECT
                COUNT(*) AS total_attempts,
                SUM(is_correct) AS correct_answers,
                SUM(score) AS total_score
            FROM ai_attempts
            WHERE user_id = ?
        """, (user_id,))

        ai_stats = cursor.fetchone()

        ai_attempts = ai_stats["total_attempts"] or 0
        ai_correct = ai_stats["correct_answers"] or 0
        ai_score = ai_stats["total_score"] or 0

        total_attempts = normal_attempts + ai_attempts
        correct_answers = normal_correct + ai_correct
        total_score = normal_score + ai_score

        accuracy = (
            correct_answers / total_attempts * 100
            if total_attempts else 0
        )

        cursor.execute("""
            SELECT
                attempts.*,
                scenarios.title,
                scenarios.attack_type,
                scenarios.difficulty
            FROM attempts
            LEFT JOIN scenarios
                ON attempts.scenario_id = scenarios.scenario_id
            WHERE attempts.user_id = ?
            ORDER BY attempts.attempted_at DESC
            LIMIT 10
        """, (user_id,))

        recent_activity = []

        for row in cursor.fetchall():
            item = dict(row)
            item["source"] = "normal"
            recent_activity.append(item)

        cursor.execute("""
            SELECT
                ai_attempts.*,
                ai_generated_scenarios.attack_type,
                ai_generated_scenarios.difficulty,
                ai_generated_scenarios.generated_content
            FROM ai_attempts
            LEFT JOIN ai_generated_scenarios
                ON ai_attempts.ai_scenario_id = ai_generated_scenarios.id
            WHERE ai_attempts.user_id = ?
            ORDER BY ai_attempts.attempted_at DESC
            LIMIT 10
        """, (user_id,))

        for row in cursor.fetchall():
            item = dict(row)
            item["source"] = "ai"

            try:
                content = json.loads(item["generated_content"])
                item["title"] = content.get(
                    "title", "AI Generated Scenario"
                )
            except (json.JSONDecodeError, TypeError):
                item["title"] = "AI Generated Scenario"

            item.pop("generated_content", None)
            recent_activity.append(item)

        recent_activity.sort(
            key=lambda item: item.get("attempted_at") or "",
            reverse=True
        )

        return jsonify({
            "user": dict(user),
            "stats": {
                "scenarios_completed": normal_completed,
                "correct_answers": correct_answers,
                "total_score": total_score,
                "accuracy": round(accuracy, 2),
                "level": calculate_level(total_score),
                "total_attempts": total_attempts,
                "normal_attempts": normal_attempts,
                "ai_attempts": ai_attempts,
                "ai_correct_answers": ai_correct,
                "ai_score": ai_score
            },
            "recent_activity": recent_activity[:10]
        })

    finally:
        connection.close()


# ============================================================
# CORS HEADERS
# ============================================================

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization"
    )
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, OPTIONS"
    )
    return response


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("=" * 45)
    print("CYBERGUARD BACKEND")
    print("=" * 45)
    print("Home:            http://localhost:5000/")
    print("Command Center:  http://localhost:5000/command-center")
    print("Analytics:       http://localhost:5000/analytics")
    print("AI Generator:    http://localhost:5000/ai-generator")
    print("Attack Radar:    http://localhost:5000/attack-radar")
    print("Frontend files:  http://localhost:5000/frontend/index.html")
    print("API Status:      http://localhost:5000/api/status")
    print("Scenarios API:   http://localhost:5000/api/scenarios")
    print("AI Generator API: http://localhost:5000/api/ai/generate")
    print("Dashboard API:   http://localhost:5000/api/dashboard/1")
    print("Analytics API:   http://localhost:5000/api/analytics/1")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
