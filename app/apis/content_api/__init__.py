from flask import Blueprint

content_bp = Blueprint('content_bp', __name__, url_prefix='/api/content')

# from . import routes

from . import routes, comments, ratings
