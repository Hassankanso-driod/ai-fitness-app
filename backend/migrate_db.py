# migrate_db.py
from sqlalchemy import text
from database import engine


def safe_add_column(conn, table: str, column_def: str):
    """
    column_def example: "prompt_version VARCHAR(20) NULL"
    """
    column_name = column_def.split()[0]
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
        conn.commit()
        print(f"[OK] Added column '{column_name}' to '{table}'")
    except Exception as e:
        msg = str(e)
        if "Duplicate column name" in msg or "already exists" in msg:
            print(f"[INFO] Column '{column_name}' already exists in '{table}'")
        else:
            print(f"[WARNING] Error adding column '{column_name}' to '{table}': {e}")


def safe_create_index(conn, index_sql: str, name: str):
    try:
        conn.execute(text(index_sql))
        conn.commit()
        print(f"[OK] Ensured index '{name}'")
    except Exception as e:
        msg = str(e)
        if "Duplicate key name" in msg or "already exists" in msg:
            print(f"[INFO] Index '{name}' already exists")
        else:
            print(f"[WARNING] Error ensuring index '{name}': {e}")


def migrate_database():
    with engine.connect() as conn:
        print("Starting database migration...\n")

        # ---- SUPPLEMENTS ----
        # Add image_urls column for multiple images support
        safe_add_column(conn, "supplements", "image_urls TEXT NULL")

        # ---- USERS (keep your existing ones if needed) ----
        safe_add_column(conn, "users", "email VARCHAR(255) NULL")
        safe_add_column(conn, "users", "email_verified BOOLEAN DEFAULT FALSE")
        safe_add_column(conn, "users", "email_verification_token VARCHAR(255) NULL")
        safe_add_column(conn, "users", "password_reset_token VARCHAR(255) NULL")
        safe_add_column(conn, "users", "password_reset_expires DATETIME NULL")
        safe_add_column(conn, "users", "active BOOLEAN DEFAULT TRUE")
        safe_add_column(conn, "users", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Create index on email for faster lookups
        safe_create_index(
            conn,
            "CREATE INDEX ix_users_email ON users (email)",
            "ix_users_email",
        )

        # ---- MEALPLANS (IMPORTANT) ----
        # Ensure old columns exist
        safe_add_column(conn, "mealplans", "carbs FLOAT NULL")
        safe_add_column(conn, "mealplans", "fat FLOAT NULL")
        safe_add_column(conn, "mealplans", "plan_json LONGTEXT NULL")

        # Professional metadata
        safe_add_column(conn, "mealplans", "prompt_version VARCHAR(20) NULL")
        safe_add_column(conn, "mealplans", "model VARCHAR(100) NULL")

        # Versioning + active
        safe_add_column(conn, "mealplans", "version INT NOT NULL DEFAULT 1")
        safe_add_column(conn, "mealplans", "is_active BOOLEAN NOT NULL DEFAULT TRUE")

        # Timestamps
        safe_add_column(conn, "mealplans", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        safe_add_column(conn, "mealplans", "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        # Indexes (fast latest plan queries)
        safe_create_index(
            conn,
            "CREATE INDEX ix_mealplans_user_created ON mealplans (user_id, created_at)",
            "ix_mealplans_user_created",
        )
        safe_create_index(
            conn,
            "CREATE INDEX ix_mealplans_user_active ON mealplans (user_id, is_active)",
            "ix_mealplans_user_active",
        )

        # ---- WORKOUT PLANS ----
        # Create workout_plans table if it doesn't exist
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workout_plans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    split VARCHAR(50) NULL,
                    days_per_week INT NULL,
                    experience VARCHAR(50) NULL,
                    goal_focus VARCHAR(50) NULL,
                    language VARCHAR(10) NULL,
                    plan_json LONGTEXT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created workout_plans table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] workout_plans table already exists")
            else:
                print(f"[WARNING] Error creating workout_plans table: {e}")
        
        # Add missing columns to workout_plans if table exists
        safe_add_column(conn, "workout_plans", "split VARCHAR(50) NULL")
        safe_add_column(conn, "workout_plans", "days_per_week INT NULL")
        safe_add_column(conn, "workout_plans", "experience VARCHAR(50) NULL")
        safe_add_column(conn, "workout_plans", "goal_focus VARCHAR(50) NULL")
        safe_add_column(conn, "workout_plans", "language VARCHAR(10) NULL")

        # ---- REMINDERS ----
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    time VARCHAR(10) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created reminders table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] reminders table already exists")
            else:
                print(f"[WARNING] Error creating reminders table: {e}")

        # ---- WATER INTAKES ----
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS water_intakes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount_ml INT NOT NULL,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created water_intakes table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] water_intakes table already exists")
            else:
                print(f"[WARNING] Error creating water_intakes table: {e}")

        # ---- WORKOUT LOGS ----
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workout_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    exercise_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NULL,
                    sets INT NOT NULL,
                    reps INT NOT NULL,
                    weight_kg FLOAT NULL,
                    duration_minutes INT NULL,
                    notes TEXT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created workout_logs table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] workout_logs table already exists")
            else:
                print(f"[WARNING] Error creating workout_logs table: {e}")

        # ---- PROGRESS ENTRIES ----
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS progress_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    weight_kg FLOAT NOT NULL,
                    bmi FLOAT NULL,
                    body_fat_percentage FLOAT NULL,
                    muscle_mass_kg FLOAT NULL,
                    notes TEXT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created progress_entries table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] progress_entries table already exists")
            else:
                print(f"[WARNING] Error creating progress_entries table: {e}")

        # ---- NOTIFICATIONS ----
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Created notifications table")
        except Exception as e:
            if "already exists" in str(e).lower() or "Duplicate table" in str(e):
                print("[INFO] notifications table already exists")
            else:
                print(f"[WARNING] Error creating notifications table: {e}")

        print("\nMigration complete!")


if __name__ == "__main__":
    migrate_database()
