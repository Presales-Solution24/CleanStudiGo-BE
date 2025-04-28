from flask import Flask
from app.extensions import db, migrate
from app.config import Config

from app.apis.auth_api import auth_bp  # blueprint sudah siap saat ini

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)

    return app
