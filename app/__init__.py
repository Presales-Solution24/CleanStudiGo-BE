from flask import Flask
from app.extensions import db, migrate
from app.config import Config

from app.apis.auth_api import auth_bp  # blueprint sudah siap saat ini
from app.apis.category_api import category_bp
from app.apis.product_api import product_bp
from app.apis.specification_api import specification_bp
from app.apis.content_api import content_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(specification_bp)
    app.register_blueprint(content_bp)

    return app
