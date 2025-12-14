# config.py
# Explanation: Database configuration for SQLAlchemy.
import os

class Config:
    # Explanation: Secret key for sessions and CSRF protection.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Explanation: SQLite database configuration (file named app.db).
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")

    # Explanation: Disable tracking modifications overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
