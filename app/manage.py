from flask import Blueprint, render_template, g, request, session
from flask import redirect, flash, url_for
from werkzeug.exceptions import abort
from .db import get_db
import functools

bp = Blueprint('manage', __name__, url_prefix='/manage')

def admin_user(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_rol'] != 'admin':
            return abort(403)
        return view(*args, **kwargs)
    return wrapped_view

@bp.route('/menu')
@admin_user
def menu():
    db = get_db()
    
    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()

    return render_template('manage/menu.html', posts=users)


@bp.route('/<string:username>/profile', methods=('GET', 'POST'))
@admin_user
def profile(username):
    db = get_db()
    posts = db.execute(
        'SELECT u.id as user_id, p.id as post_id, title, body, created, author_id, username'
        ' FROM user u'
        ' LEFT JOIN post p ON p.author_id = u.id'
        ' WHERE u.username = ?',
        (username,)
    ).fetchall()

    return render_template('/manage/profile.html', posts=posts)


@bp.route('/<string:username>/create', methods=('GET', 'POST'))
@admin_user
def create(username):
    if request.method == 'POST':
        # recieve the data of form
        title = request.form['title']
        body = request.form['body']

        print(f'Title: {title}, Body: {body}')

        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            # recieve the object db connect
            db = get_db()

            user_id = db.execute(
            'SELECT id FROM user'
            ' WHERE username = ?',
            (username,)
            ).fetchall()

            # insert the data of post
            db.execute(
                """INSERT INTO post (author_id, body, title)
                VALUES (?, ?, ?)""", 
                (user_id[0]['id'], body, title),
            )
            db.commit() # save the change or the insert on db

            print(username, 'username muestra')

            return redirect(url_for('blog.index'))
        
        flash(error)
    return render_template('/blog/create.html')