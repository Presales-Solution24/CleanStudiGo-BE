from functools import wraps
from flask import request, jsonify
from app.utils.token_utils import decode_token
from app.models.auth_models.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        user_id = decode_token(token)

        if not user_id:
            return jsonify({'message': 'Invalid or expired token!'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found!'}), 404

        return f(user, *args, **kwargs)

    return decorated
