from flask import request, jsonify
from app.apis.auth_api import auth_bp
from app.models.auth_models.models import User
from app.extensions import db
from app.utils.token_utils import generate_token, decode_token

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'message': 'User already exists'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    print(user)
    print(password)

    if user and user.check_password(password):
        print('bener')
        token = generate_token(user.id)
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    # Ambil Authorization header
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    # Buang "Bearer " prefix jika ada
    if token.startswith('Bearer '):
        token = token[7:]

    # Decode token untuk mendapatkan user_id
    user_id = decode_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid or expired token'}), 401

    # Ambil input dari JSON body
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    # Validasi input
    if not old_password or not new_password:
        return jsonify({'message': 'Both old_password and new_password are required'}), 400

    # Cari user berdasarkan user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Verifikasi old password
    if not user.check_password(old_password):
        return jsonify({'message': 'Old password is incorrect'}), 401

    # Set new password
    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200