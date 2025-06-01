from flask import Blueprint

textcontent_bp = Blueprint('textcontent_bp', __name__, url_prefix='/api/text')

from . import routes  # routes.py akan menggunakan `auth_bp` ini
