from flask import (
    Blueprint, flash, g, redirect, render_template, request,
    url_for, jsonify
)
from . import db
from .auth import token_required

bp = Blueprint('blog', __name__, url_prefix='/api/blog')


@bp.route('/', methods=['GET'])
def index():
    """获取所有帖子列表"""
    posts = db.query_db(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    return jsonify(posts)


@bp.route('/<int:id>', methods=['GET'])
def get_post_detail(id):
    """获取帖子详情"""
    post = db.query_db(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,),
        one=True
    )

    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    # # 获取评论
    # comments = db.query_db(
    #     'SELECT c.id, content, created, author_id, username'
    #     ' FROM comment c JOIN user u ON c.author_id = u.id'
    #     ' WHERE post_id = %s'
    #     ' ORDER BY created DESC',
    #     (id,)
    # )
    #
    # post['comments'] = comments
    return jsonify(post)


@bp.route('/', methods=['POST'])
@token_required
def create():
    """创建新帖子"""
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({'error': error}), 400

    try:
        db.query_db(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (%s, %s, %s)',
            (title, body, g.user['id'])
        )
        return jsonify({'message': 'Post created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update(id):
    """更新帖子"""
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({'error': error}), 400

    try:
        db.query_db(
            'UPDATE post SET title = %s, body = %s'
            ' WHERE id = %s AND author_id = %s',
            (title, body, id, g.user['id'])
        )
        return jsonify({'message': 'Post updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete(id):
    """删除帖子"""
    try:
        db.query_db(
            'DELETE FROM post WHERE id = %s AND author_id = %s',
            (id, g.user['id'])
        )
        return jsonify({'message': 'Post deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


