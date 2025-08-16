from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from models.user import User
from database import db

auth_bp = Blueprint('auth', __name__)

# auth routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request'})

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request'}), 401

    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    return jsonify({'message': 'Bad username or password'}), 401

