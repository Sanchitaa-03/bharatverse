"""
app.py
-------
This is the MAIN entry point of the BharatVerse Flask application.

BEGINNER NOTE:
Flask = a Python framework that helps us build the backend (server-side
logic) of our website. Running this file starts a local web server that
your browser can talk to at http://127.0.0.1:5000

This file mainly WIRES THINGS TOGETHER:
- It creates the Flask app
- It registers each "Blueprint" (group of related routes) from routes/
- It defines a couple of simple top-level routes (landing page, 404)
"""

import os
from flask import Flask, render_template, session, redirect, url_for, send_from_directory

from config import Config
from database.init_db import initialize_database, ensure_student_demo_account, DB_PATH
from models import models

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.realms import realms_bp
from routes.game import game_bp
from routes.map import map_bp
from routes.timeline import timeline_bp
from routes.leaderboard import leaderboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure the database exists and has starting data before the
    # app starts handling requests. Safe to call every time - it only
    # inserts data that doesn't already exist (uses INSERT OR IGNORE).
    if not os.path.exists(DB_PATH):
        initialize_database()
    ensure_student_demo_account()

    # Register all route groups (blueprints)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(realms_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(leaderboard_bp)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard.dashboard"))
        return render_template("index.html", realms=models.get_all_realms())

    @app.route("/image.png")
    def brand_logo():
        return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "image.png")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" makes it reachable from other devices on the same
    # network (useful for demoing on a phone). Remove for stricter local-only use.
    app.run(debug=True, host="0.0.0.0", port=5000)
