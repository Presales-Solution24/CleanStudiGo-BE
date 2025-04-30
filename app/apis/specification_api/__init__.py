from flask import Blueprint

specification_bp = Blueprint('specification_bp', __name__, url_prefix='/api/specification')

from . import routes
