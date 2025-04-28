from flask import Blueprint, request, jsonify
from app.models.auth_models import User
from app.utils.token_utils import decode_token

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token missing'}), 401

    user_id = decode_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token'}), 401

    user = User.query.get(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200
