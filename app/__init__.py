from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth_routes, dashboard_routes
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(dashboard_routes.dashboard_bp)

    return app
