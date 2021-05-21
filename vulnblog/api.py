from flask import request, Blueprint, jsonify, abort, g

from vulnblog.auth import api_auth
from vulnblog.db import get_db, get_post

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/', methods=('GET',))
def index():
    db = get_db()

    order = request.args.get('order') if request.args.get('order') is not None else 'created DESC'
    if len(order.split(' ')) < 2:
        abort(403, f'order by clause is needed in the format \'column direction\'. eg: created DESC')

    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        f' ORDER BY {order}'
    ).fetchall()

    result = [dict(row) for row in posts]

    return jsonify(result)


@bp.route('/create', methods=('POST',))
@api_auth.login_required
def create():
    data = request.json

    if 'title' not in data or len(data['title']) <= 0:
        return jsonify({'error': 'a title is required'})

    if 'body' not in data or len(data['body']) <= 0:
        return jsonify({'error': 'a body is required'})

    db = get_db()
    res = db.execute(
        'INSERT INTO post (title, body, author_id)'
        ' VALUES (?, ?, ?)',
        (data['title'], data['body'], g.user['id'])
    )
    db.commit()

    return jsonify({'blog_id': f'{res.lastrowid}'})


@bp.route('/post/<int:post_id>', methods=('GET', 'PUT', 'DELETE'))
@api_auth.login_required
def update(post_id):
    if request.method == 'DELETE':
        get_post(post_id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (post_id,))
        db.commit()
        return jsonify('ok')

    if request.method == 'PUT':
        post = get_post(post_id, False)
        data = request.json

        title = post.title if ('title' not in data or len(data['title']) <= 0) else data['title']
        body = post.body if ('body' not in data or len(data['body']) <= 0) else data['body']

        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, post_id)
        )
        db.commit()

        return jsonify('ok')

    post = get_post(post_id, False)
    return jsonify(dict(post))
