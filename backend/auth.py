import functools
from flask import (
    Blueprint, g, request, jsonify, current_app
)
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import pymysql
from werkzeug.exceptions import abort

from backend.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            db = get_db()
            cursor = db.execute(
                'SELECT * FROM user WHERE id = %s', (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
                
            g.user = user
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed):
    return hash_password(password) == hashed

def generate_token(user_id):
    return create_token(user_id)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        db = get_db()
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (%s, %s)",
                (username, hash_password(password))
            )
            db.commit()
        except pymysql.IntegrityError:
            error = f"User {username} is already registered."
        except Exception as e:
            error = str(e)
        else:
            return jsonify({'message': 'Registration successful'}), 201

    return jsonify({'error': error}), 400

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        db = get_db()
        cursor = db.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password(password, user['password']):
            error = 'Incorrect password.'

    if error is None:
        token = generate_token(user['id'])
        return jsonify({
            'token': token,
            'username': user['username'],
            'user_id': user['id']
        })

    return jsonify({'error': error}), 400

@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Logged out successfully'})

@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({
        'id': g.user['id'],
        'username': g.user['username']
    })