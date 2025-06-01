from flask import Flask, send_from_directory
from app.extensions import db, migrate
from app.config import Config

from app.apis.auth_api import auth_bp
from app.apis.category_api import category_bp
from app.apis.product_api import product_bp
from app.apis.specification_api import specification_bp
from app.apis.content_api import content_bp
from app.apis.dashboard_api import dashboard_bp
from app.apis.textcontent_api import textcontent_bp
from flask_cors import CORS

import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(specification_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(textcontent_bp)


    # Serve uploaded files from /uploads/<path:filename>
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_path = os.path.join(app.root_path, 'uploads')
        return send_from_directory(upload_path, filename)

    return app
