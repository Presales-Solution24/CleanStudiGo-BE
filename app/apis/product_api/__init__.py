from flask import Blueprint

product_bp = Blueprint('product_bp', __name__, url_prefix='/api/product')

from . import routes
