from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from vulnblog.auth import login_required
from vulnblog.db import get_db, get_post

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'GET':
        return render_template('blog/create.html')

    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, g.user['id'])
        )
        db.commit()

    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method == 'GET':
        return render_template('blog/update.html', post=post)

    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, post_id)
        )
        db.commit()

    return redirect(url_for('blog.index'))


@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    get_post(post_id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()
    return redirect(url_for('blog.index'))
