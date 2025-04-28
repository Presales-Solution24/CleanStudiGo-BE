from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

from . import routes  # routes.py akan menggunakan `auth_bp` ini
