import json
from pathlib import Path

from database import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = BASE_DIR / "data" / "scenarios.json"


def load_scenarios_from_json():
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def import_scenarios():
    scenarios = load_scenarios_from_json()

    connection = get_connection()
    cursor = connection.cursor()

    imported = 0

    for scenario in scenarios:

        existing = cursor.execute(
            """
            SELECT scenario_id
            FROM scenarios
            WHERE title = ?
            """,
            (scenario["title"],)
        ).fetchone()

        if existing:
            continue

        cursor.execute(
            """
            INSERT INTO scenarios (
                attack_type,
                title,
                difficulty,
                scenario_text,
                correct_answer,
                explanation,
                defence_tip
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario["attack_type"],
                scenario["title"],
                scenario["difficulty"],
                scenario["scenario_text"],
                scenario["correct_answer"],
                scenario["explanation"],
                scenario["defence_tip"]
            )
        )

        imported += 1

    connection.commit()
    connection.close()

    print(f"✅ {imported} scenarios imported successfully!")


def get_all_scenarios():

    connection = get_connection()

    scenarios = connection.execute(
        """
        SELECT *
        FROM scenarios
        ORDER BY scenario_id
        """
    ).fetchall()

    connection.close()

    return scenarios


if __name__ == "__main__":
    import_scenarios()

    scenarios = get_all_scenarios()

    print(f"📊 Total scenarios in database: {len(scenarios)}")