from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 注册逻辑
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing username, email, or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 409

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

# 登录逻辑
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate JWT Token
    token = jwt.encode(
        {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Token expires in 1 hour
        },
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({
        'message': 'Logged in successfully!',
        'token': token
    }), 200