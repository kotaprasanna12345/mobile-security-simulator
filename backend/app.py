
import os
import json
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from database import get_connection
from ai_engine import generate_scenario


# ==========================================
# CYBERGUARD - MOBILE SECURITY SIMULATOR
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

app = Flask(__name__)

# Frontend folder location
app.config["FRONTEND_DIR"] = str(FRONTEND_DIR)


# ==========================================
# 1. HOME PAGE
# ==========================================

@app.route("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "command-center.html")


# ==========================================
# 2. FRONTEND PAGE ROUTES
# ==========================================

@app.route("/command-center")
def command_center():
    return send_from_directory(str(FRONTEND_DIR), "command-center.html")


@app.route("/analytics")
def analytics():
    return send_from_directory(str(FRONTEND_DIR), "analytics.html")


@app.route("/ai-generator")
def ai_generator():
    return send_from_directory(str(FRONTEND_DIR), "ai-generator.html")


@app.route("/attack-radar")
def attack_radar():
    return send_from_directory(str(FRONTEND_DIR), "attack-radar.html")


# ==========================================
# 3. STATIC FILES - CSS, JS, IMAGES
# ==========================================

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(str(FRONTEND_DIR), filename)


# ==========================================
# 4. BACKEND HEALTH CHECK
# ==========================================

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "online",
        "message": "CyberGuard Backend is Running",
        "version": "2.1"
    })


# ==========================================
# 5. GET ALL SCENARIOS
# ==========================================

@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM scenarios")
        rows = cursor.fetchall()

        scenarios = []

        for row in rows:
            if hasattr(row, "keys"):
                scenario = dict(row)
            else:
                columns = [column[0] for column in cursor.description]
                scenario = dict(zip(columns, row))

            # Convert JSON text fields into Python data
            for key in ("options", "correct_answer", "explanation"):
                if key in scenario and isinstance(scenario[key], str):
                    try:
                        scenario[key] = json.loads(scenario[key])
                    except (json.JSONDecodeError, TypeError):
                        pass

            scenarios.append(scenario)

        connection.close()

        return jsonify({
            "status": "success",
            "count": len(scenarios),
            "scenarios": scenarios
        })

    except Exception as error:
        app.logger.exception("Unable to fetch scenarios")
        return jsonify({
            "status": "error",
            "message": "Unable to fetch scenarios",
            "details": str(error)
        }), 500


# ==========================================
# 6. GET ONE SCENARIO
# ==========================================

@app.route("/api/scenarios/<int:scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM scenarios WHERE id = ?",
            (scenario_id,)
        )

        row = cursor.fetchone()
        connection.close()

        if row is None:
            return jsonify({
                "status": "error",
                "message": "Scenario not found"
            }), 404

        if hasattr(row, "keys"):
            scenario = dict(row)
        else:
            columns = [column[0] for column in cursor.description]
            scenario = dict(zip(columns, row))

        for key in ("options", "correct_answer", "explanation"):
            if key in scenario and isinstance(scenario[key], str):
                try:
                    scenario[key] = json.loads(scenario[key])
                except (json.JSONDecodeError, TypeError):
                    pass

        return jsonify({
            "status": "success",
            "scenario": scenario
        })

    except Exception as error:
        app.logger.exception("Unable to fetch scenario")
        return jsonify({
            "status": "error",
            "message": "Unable to fetch scenario",
            "details": str(error)
        }), 500


# ==========================================
# 7. AI SCENARIO GENERATOR
# ==========================================

@app.route("/api/ai-generator", methods=["POST"])
def ai_scenario_generator():
    try:
        data = request.get_json(silent=True) or {}

        # Pass the user's request to the existing AI engine
        scenario = generate_scenario(data)

        return jsonify({
            "status": "success",
            "scenario": scenario
        })

    except Exception as error:
        app.logger.exception("Scenario generation failed")
        return jsonify({
            "status": "error",
            "message": "Scenario generation failed",
            "details": str(error)
        }), 500


# ==========================================
# 8. CORS HEADERS
# ==========================================

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


# ==========================================
# 9. RUN SERVER
# ==========================================

if __name__ == "__main__":
    print("=" * 45)
    print("CYBERGUARD BACKEND")
    print("=" * 45)
    print("Home:          http://127.0.0.1:5000/")
    print("Command Center: http://127.0.0.1:5000/command-center")
    print("Analytics:     http://127.0.0.1:5000/analytics")
    print("AI Generator:  http://127.0.0.1:5000/ai-generator")
    print("Attack Radar:  http://127.0.0.1:5000/attack-radar")
    print("Health Check:  http://127.0.0.1:5000/api/status")
    print("=" * 45)

    app.run(host="127.0.0.1", port=5000, debug=True)
