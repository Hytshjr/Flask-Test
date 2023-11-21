from flask import Blueprint, render_template, g, request
from flask import url_for, flash, session, redirect
from werkzeug.exceptions import abort
from .auth import logged_required
from .db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db() # recieve the db connection
    # give the data of posts and user
    posts=db.execute(
            'SELECT p.id, title, body, created, author_id, username, rol'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ).fetchall()
    
    return render_template('/blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@logged_required
def create():
    if request.method == 'POST':
        # recieve the data of form
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            # recieve the object db connect
            db = get_db()

            # insert the data of post
            db.execute(
                """INSERT INTO post (author_id, body, title)
                VALUES (?, ?, ?)""", 
                (session['user_id'], body, title),
            )
            db.commit() # save the change or the insert on db

            return redirect(url_for('blog.index'))
        
        flash(error)

    return render_template('/blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@logged_required
def update(id):
    posts = get_post(id)

    if request.method == 'POST':
        # recieve the data of form
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'

        
        if error is not None:

            flash(error)
        
        else:

            # recieve the object db connect
            db = get_db()

            # insert the data of post
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
            )
            db.commit() # save the change or the insert on db

            return redirect(url_for('blog.index'))

    return render_template('/blog/update.html', posts=posts)


def get_post(id, check_author=True):
    db = get_db()
    # recieve the post
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # validate if the post exists
    if posts is None:
        abort(404, f"Post id {id} doesn't exist.")

    # validate if user is author
    if check_author and posts['author_id'] != session['user_id'] and session['user_rol'] !='admin':
        abort(403)

    return posts


@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@logged_required
def delete_post(id):
    posts = get_post(id)

    if posts['author_id'] == session['user_id'] or session['user_rol'] == 'admin':
        db = get_db()
        db.execute(
            'DELETE FROM post WHERE id = ?', (id,)
        )
        db.commit()

    return redirect(url_for('blog.index'))

    