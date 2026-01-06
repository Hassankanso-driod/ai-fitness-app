# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# 1) Prefer a full DATABASE_URL if provided (best for AWS / flexible)
DATABASE_URL = _env("DATABASE_URL").strip()

# 2) If DATABASE_URL not set, use a simple switch:
#    DB_DIALECT=sqlite  -> use SQLite (local dev)
#    DB_DIALECT=mysql   -> use MySQL (default)
DB_DIALECT = _env("DB_DIALECT", "mysql").strip().lower()

# --- Build DATABASE_URL if not provided ---
if not DATABASE_URL:
    if DB_DIALECT == "sqlite":
        # ✅ Always resolve SQLite path relative to THIS FILE (backend folder),
        # not relative to where uvicorn is executed.
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Folder to store sqlite db
        DB_DIR = os.path.join(BASE_DIR, "database")
        os.makedirs(DB_DIR, exist_ok=True)

        # Allow override by env, but still resolve safely
        # If SQLITE_PATH is relative => make it relative to BASE_DIR
        raw_sqlite_path = _env("SQLITE_PATH", "database/fitness_ai.db").strip()

        if os.path.isabs(raw_sqlite_path):
            sqlite_path = raw_sqlite_path
        else:
            sqlite_path = os.path.join(BASE_DIR, raw_sqlite_path)

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

        # Windows safety: normalize
        sqlite_path = os.path.normpath(sqlite_path)

        DATABASE_URL = f"sqlite:///{sqlite_path}"

        print(f"[DB] Using SQLite at: {sqlite_path}")

    else:
        # MySQL fallback env vars
        MYSQL_USER = _env("MYSQL_USER", "root")
        MYSQL_PASSWORD = _env("MYSQL_PASSWORD", "")
        MYSQL_HOST = _env("MYSQL_HOST", "127.0.0.1")
        MYSQL_PORT = _env("MYSQL_PORT", "3306")
        MYSQL_DATABASE = _env("MYSQL_DATABASE", "fitness_ai")

        DATABASE_URL = (
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )

# --- Engine options depending on dialect ---
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

# SQLite needs this option (threading)
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_recycle"] = 3600

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
