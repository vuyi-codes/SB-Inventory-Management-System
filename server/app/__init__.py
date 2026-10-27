import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import event
from werkzeug.exceptions import HTTPException

import app.models
from app.api import api
from app.config import CONFIGS
from app.extensions import db, migrate
from app.logging_config import configure_logging
from app.seed import seed_demo_accounts, seed_demo_data




def create_app(config=None):
    server_directory = Path(__file__).resolve().parent.parent
    load_dotenv(server_directory / ".env")
    load_dotenv(server_directory.parent / ".env")
    configure_logging()

    app = Flask(__name__)
    configured_environment = (
        config.get("APP_ENV")
        if isinstance(config, dict)
        else getattr(config, "APP_ENV", None)
    )
    environment = (
        configured_environment or os.getenv("APP_ENV", "development")
    ).lower()
    if environment not in CONFIGS:
        raise ValueError("APP_ENV must be development, production, or testing")
    app.config.from_object(CONFIGS[environment])
    app.config["APP_ENV"] = environment

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    environment = app.config.get("APP_ENV", environment).lower()
    if environment not in CONFIGS:
        raise ValueError("APP_ENV must be development, production, or testing")
    app.config["APP_ENV"] = environment

    if config is None or (
        isinstance(config, dict) and "SECRET_KEY" not in config
    ):
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or app.config["SECRET_KEY"]

    for setting in (
        "OAUTH_FRONTEND_URL",
        "OAUTH_BACKEND_URL",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "APPLE_CLIENT_ID",
        "APPLE_CLIENT_SECRET",
        "APPLE_TEAM_ID",
        "APPLE_KEY_ID",
        "APPLE_PRIVATE_KEY",
    ):
        if setting not in app.config:
            app.config[setting] = os.getenv(setting)
    app.config["OAUTH_FRONTEND_URL"] = (
        app.config["OAUTH_FRONTEND_URL"] or "http://localhost:3000"
    ).rstrip("/")
    app.config["OAUTH_BACKEND_URL"] = (
        app.config["OAUTH_BACKEND_URL"] or "http://localhost:8000"
    ).rstrip("/")
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

    database_variables = {
        "development": ("DEVELOPMENT_DATABASE_URL",),
        "testing": ("TEST_DATABASE_URL",),
        "production": ("PRODUCTION_DATABASE_URL",),
    }
    explicit_database_uri = isinstance(config, dict) and (
        "SQLALCHEMY_DATABASE_URI" in config
    )
    if not explicit_database_uri:
        database_url = next(
            (
                os.getenv(variable)
                for variable in database_variables[environment]
                if os.getenv(variable)
            ),
            None,
        )
        if database_url:
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    database_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql+psycopg2://", 1
            )
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    if environment == "production":
        missing = [
            name
            for name, value in (
                ("SECRET_KEY", app.config.get("SECRET_KEY")),
                (
                    "PRODUCTION_DATABASE_URL",
                    app.config.get("SQLALCHEMY_DATABASE_URI"),
                ),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Missing required production configuration: " + ", ".join(missing)
            )
    elif environment == "development":
        missing = [
            name
            for name, value in (
                ("SECRET_KEY", app.config.get("SECRET_KEY")),
                (
                    "DEVELOPMENT_DATABASE_URL",
                    app.config.get("SQLALCHEMY_DATABASE_URI"),
                ),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Missing required development configuration: " + ", ".join(missing)
            )
    secret_key = app.config.get("SECRET_KEY")
    if secret_key is not None and (
        not isinstance(secret_key, str) or len(secret_key.encode("utf-8")) < 32
    ):
        raise RuntimeError("SECRET_KEY must be at least 32 bytes long")
    db.init_app(app)
    with app.app_context():
        engine = db.engine
        if engine.dialect.name == "sqlite":
            event.listen(engine, "connect", enable_sqlite_foreign_keys)
    migrate.init_app(
        app,
        db,
        directory=str(server_directory / "migrations"),
    )
    app.register_blueprint(api, url_prefix="/api")
    register_error_handlers(app)
    register_database_commands(app)
    return app


def enable_sqlite_foreign_keys(connection, _record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def register_database_commands(app):
    @app.cli.command("seed-demo-accounts")
    def seed_demo_accounts_command():
        """Create local demo manager and stock-controller accounts."""
        if app.config["APP_ENV"] == "production":
            raise RuntimeError("Demo accounts cannot be created in production")
        if seed_demo_accounts():
            app.logger.info("Demo manager and stock-controller accounts created")
        else:
            app.logger.info("Demo accounts already exist; no changes made")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Add sample clothing-store inventory and transactions."""
        if app.config["APP_ENV"] == "production":
            raise RuntimeError("Demo data cannot be seeded in production")
        if seed_demo_data():
            app.logger.info("Demo data added")
        else:
            app.logger.info("Demo data already exists; no changes made")


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = error.get_response()
        response.set_data(app.json.dumps({"error": error.description}))
        response.content_type = app.json.mimetype
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error")
        return {"error": "Internal server error"}, 500
