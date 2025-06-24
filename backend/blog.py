from flask import (
    Blueprint, g, request, jsonify
)
import pymysql
from werkzeug.exceptions import abort

from backend.auth import token_required
from backend.db import get_db

bp = Blueprint('blog', __name__, url_prefix='/api/blog')

@bp.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = cursor.fetchall()

    return jsonify({
        'posts': [{
            'id': post['id'],
            'title': post['title'],
            'body': post['body'],
            'created': post['created'],
            'author_id': post['author_id'],
            'username': post['username']
        } for post in posts]
    })

@bp.route('/', methods=['POST'])
@token_required
def create():
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({'error': error}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (%s, %s, %s)',
            (title, body, g.user['id'])
        )
        db.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Post created successfully'}), 201

def get_post(id, check_author=True):
    db = get_db()
    cursor = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = cursor.fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update(id):
    post = get_post(id)
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({'error': error}), 400

    db = get_db()
    try:
        db.execute(
            'UPDATE post SET title = %s, body = %s'
            ' WHERE id = %s',
            (title, body, id)
        )
        db.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Post updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete(id):
    get_post(id)
    db = get_db()
    try:
        db.execute('DELETE FROM post WHERE id = %s', (id,))
        db.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Post deleted successfully'})

@bp.route('/<int:id>', methods=['GET'])
def get_post_detail(id):
    post = get_post(id, check_author=False)
    return jsonify({
        'id': post['id'],
        'title': post['title'],
        'body': post['body'],
        'created': post['created'],
        'author_id': post['author_id'],
        'username': post['username']
    })