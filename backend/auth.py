import os
import jwt
import datetime
from functools import wraps
from flask import (
    Blueprint, flash, g, redirect, render_template, request,
    session, url_for, jsonify, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from . import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def hash_password(password):
    return generate_password_hash(password)


def check_password(hash, password):
    return check_password_hash(hash, password)


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.query_db(
                'SELECT * FROM user WHERE id = %s',
                (data['user_id'],),
                one=True
            )
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
            g.user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated


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
        try:
            db.query_db(
                'INSERT INTO user (username, password) VALUES (%s, %s)',
                (username, hash_password(password))
            )
        except Exception as e:
            error = f"User {username} is already registered."
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
        user = db.query_db(
            'SELECT * FROM user WHERE username = %s',
            (username,),
            one=True
        )

        if user is None:
            error = 'Incorrect username.'
        elif not check_password(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            token = generate_token(user['id'])
            return jsonify({
                'token': token,
                'username': user['username'],
                'user_id': user['id']
            })

    return jsonify({'error': error}), 401


@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Successfully logged out'})


@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({
        'id': g.user['id'],
        'username': g.user['username']
    })
