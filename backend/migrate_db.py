# migrate_db.py
from sqlalchemy import text
from database import engine

def safe_add_column(conn, table, column_def):
    """Safely add a column only if it does not exist"""
    column_name = column_def.split()[0]
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
        conn.commit()
        print(f"[OK] Added column '{column_name}' to '{table}'")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"[INFO] Column '{column_name}' already exists in '{table}'")
        else:
            print(f"[WARNING] Error adding column '{column_name}' to '{table}': {e}")


def safe_create_table(conn, create_sql, table_name):
    """Safely create table"""
    try:
        conn.execute(text(create_sql))
        conn.commit()
        print(f"[OK] Ensured table '{table_name}' exists")
    except Exception as e:
        print(f"[WARNING] Error creating table '{table_name}': {e}")


def migrate_database():
    with engine.connect() as conn:
        print("🔧 Starting database migration...\n")

        # -----------------------
        # USERS TABLE FIXES
        # -----------------------
        safe_add_column(conn, "users", "email VARCHAR(100)")
        safe_add_column(conn, "users", "active BOOLEAN DEFAULT TRUE")
        safe_add_column(conn, "users", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # -----------------------
        # SUPPLEMENTS TABLE FIXES
        # -----------------------
        safe_add_column(conn, "supplements", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # -----------------------
        # FAVORITES TABLE FIXES
        # -----------------------
        safe_add_column(conn, "favorites", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # -----------------------
        # MEALPLANS TABLE FIXES
        # -----------------------
        safe_add_column(conn, "mealplans", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # -----------------------
        # NOTIFICATIONS TABLE FIXES
        # -----------------------
        safe_add_column(conn, "notifications", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # -----------------------
        # CREATE workout_logs TABLE
        # -----------------------
        safe_create_table(conn, """
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER,
                exercise_name VARCHAR(255),
                category VARCHAR(50),
                sets INTEGER,
                reps INTEGER,
                weight_kg FLOAT,
                duration_minutes INTEGER,
                notes VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """, "workout_logs")

        # -----------------------
        # CREATE progress_entries TABLE
        # -----------------------
        safe_create_table(conn, """
            CREATE TABLE IF NOT EXISTS progress_entries (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER,
                weight_kg FLOAT,
                bmi FLOAT,
                body_fat_percentage FLOAT,
                muscle_mass_kg FLOAT,
                notes VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """, "progress_entries")

        print("\n✅ Migration complete! Database is now synced with models.py")


if __name__ == "__main__":
    migrate_database()
