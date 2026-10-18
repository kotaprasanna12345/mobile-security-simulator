
import os
import json

from flask import (
    Flask,
    render_template,
    send_from_directory,
    jsonify,
    request
)

from database import get_connection
from ai_engine import generate_scenario


# ==========================================
# CYBERGUARD BACKEND CONFIGURATION
# ==========================================

frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../frontend")
)

app = Flask(
    __name__,
    template_folder=frontend_dir,
    static_folder=frontend_dir
)


# ==========================================
# 1. MAIN HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("command-center.html")


# ==========================================
# 2. SPECIFIC HTML PAGES
# ==========================================

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


# ==========================================
# 3. STATIC FILES: CSS, JS, IMAGES
# ==========================================

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(frontend_dir, filename)


# ==========================================
# 4. BACKEND HEALTH CHECK API
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
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM scenarios")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        scenarios = []

        for row in rows:
            if hasattr(row, "keys"):
                scenario = dict(row)
            else:
                scenario = dict(zip(columns, row))

            for key in ("options", "correct_answer", "explanation"):
                if key in scenario and isinstance(scenario[key], str):
                    try:
                        scenario[key] = json.loads(scenario[key])
                    except (json.JSONDecodeError, TypeError):
                        pass

            scenarios.append(scenario)

        return jsonify({
            "status": "success",
            "count": len(scenarios),
            "scenarios": scenarios
        })

    except Exception as error:
        app.logger.exception("Error fetching scenarios")

        return jsonify({
            "status": "error",
            "message": "Unable to fetch scenarios",
            "details": str(error)
        }), 500

    finally:
        if connection is not None:
            connection.close()


# ==========================================
# 6. GET A SINGLE SCENARIO
# ==========================================

@app.route("/api/scenarios/<int:scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM scenarios WHERE id = ?",
            (scenario_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "status": "error",
                "message": "Scenario not found"
            }), 404

        columns = [column[0] for column in cursor.description]

        if hasattr(row, "keys"):
            scenario = dict(row)
        else:
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
        app.logger.exception("Error fetching scenario")

        return jsonify({
            "status": "error",
            "message": "Unable to fetch scenario",
            "details": str(error)
        }), 500

    finally:
        if connection is not None:
            connection.close()


# ==========================================
# 7. AI SCENARIO GENERATOR
# ==========================================

@app.route("/api/ai-generator", methods=["POST"])
def ai_scenario_generator():
    try:
        data = request.get_json(silent=True) or {}

        scenario = generate_scenario(data)

        return jsonify({
            "status": "success",
            "scenario": scenario
        })

    except Exception as error:
        app.logger.exception("AI scenario generation failed")

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
# 9. START SERVER
# ==========================================

if __name__ == "__main__":
    print("=" * 45)
    print("CYBERGUARD BACKEND")
    print("=" * 45)
    print("Home:           http://127.0.0.1:5000/")
    print("Command Center: http://127.0.0.1:5000/command-center")
    print("Analytics:      http://127.0.0.1:5000/analytics")
    print("AI Generator:   http://127.0.0.1:5000/ai-generator")
    print("Attack Radar:   http://127.0.0.1:5000/attack-radar")
    print("API Status:     http://127.0.0.1:5000/api/status")
    print("Scenarios API:  http://127.0.0.1:5000/api/scenarios")
    print("=" * 45)

    app.run(debug=True)
