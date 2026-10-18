import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "simulator.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a database connection."""

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():
    """Create all required CyberGuard database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # 1. USERS TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            user_id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # 2. ADD PASSWORD COLUMN TO EXISTING USERS TABLE
    # ========================================================

    # Existing database ni delete cheyyakunda password_hash
    # column add chestunnam.

    try:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN password_hash TEXT
        """)

        print("✅ password_hash column added to users table.")

    except sqlite3.OperationalError:

        # Column already exists
        print("ℹ️ password_hash column already exists.")


    # ========================================================
    # 3. FIXED CYBERSECURITY SCENARIOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (

            scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,

            attack_type TEXT NOT NULL,

            title TEXT NOT NULL,

            difficulty TEXT NOT NULL,

            scenario_text TEXT NOT NULL,

            correct_answer TEXT NOT NULL,

            explanation TEXT NOT NULL,

            defence_tip TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # 4. NORMAL USER ATTEMPTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (

            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            scenario_id INTEGER,

            selected_answer TEXT NOT NULL,

            is_correct INTEGER NOT NULL,

            score INTEGER DEFAULT 0,

            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (scenario_id)
                REFERENCES scenarios(scenario_id)

        )
    """)


    # ========================================================
    # 5. USER PROGRESS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (

            user_id INTEGER PRIMARY KEY,

            scenarios_completed INTEGER DEFAULT 0,

            correct_answers INTEGER DEFAULT 0,

            total_score INTEGER DEFAULT 0,

            accuracy REAL DEFAULT 0,

            level TEXT DEFAULT 'Security Beginner',

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)

        )
    """)


    # ========================================================
    # 6. AI GENERATED SCENARIOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_generated_scenarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            attack_type TEXT NOT NULL,

            difficulty TEXT NOT NULL,

            prompt TEXT,

            generated_content TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # 7. AI SCENARIO ATTEMPTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_attempts (

            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            ai_scenario_id INTEGER,

            selected_answer TEXT NOT NULL,

            correct_answer TEXT NOT NULL,

            is_correct INTEGER NOT NULL,

            score INTEGER DEFAULT 0,

            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (ai_scenario_id)
                REFERENCES ai_generated_scenarios(id)

        )
    """)


    # ========================================================
    # 8. CREATE / UPDATE CYBERGUARD USER
    # ========================================================

    # Existing Sai Prasanna user ni preserve chestham.
    # User lekapothe create chestham.

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE user_id = 1
    """)

    existing_user = cursor.fetchone()


    if existing_user:

        # Existing User ID 1 ki password set chestham.

        password_hash = generate_password_hash("sp@1619")

        cursor.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE user_id = 1
        """, (password_hash,))

        print("✅ Password updated for User ID 1.")


    else:

        # User ID 1 lekapothe Sai Prasanna create chestham.

        password_hash = generate_password_hash("sp@1619")

        cursor.execute("""
            INSERT INTO users
            (
                user_id,
                username,
                password_hash
            )
            VALUES
            (
                1,
                'Sai Prasanna',
                ?
            )
        """, (password_hash,))

        print("✅ Sai Prasanna user created.")


    # ========================================================
    # SAVE CHANGES
    # ========================================================

    connection.commit()

    connection.close()


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    print()
    print("==============================================")
    print("🛡️  CYBERGUARD DATABASE")
    print("==============================================")
    print("✅ Database tables created successfully!")
    print()
    print("📁 Database location:")
    print(f"   {DB_PATH}")
    print()
    print("📊 Tables:")
    print("   ✓ users")
    print("   ✓ scenarios")
    print("   ✓ attempts")
    print("   ✓ progress")
    print("   ✓ ai_generated_scenarios")
    print("   ✓ ai_attempts")
    print()
    print("🔐 LOGIN SYSTEM")
    print("   ✓ User ID: 1")
    print("   ✓ Username: Sai Prasanna")
    print("   ✓ Password: Configured")
    print("   ✓ Password stored securely as hash")
    print()
    print("🤖 AI attempt tracking is ready!")
    print("==============================================")
    print()


# ============================================================
# RUN DATABASE SETUP
# ============================================================

if __name__ == "__main__":
    create_tables()