from flask import Blueprint, render_template, request, session
from flask import redirect, flash, g, url_for
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
    # recieve the conection
    db = get_db()
    db.execute('SELECT * FROM user') # recieve the query
    users = db.fetchall()

    return render_template('manage/menu.html', posts=users)


@bp.route('/<string:username>/profile', methods=('GET', 'POST'))
@admin_user
def profile(username):
    db = get_db()
    db.execute(
        'SELECT u.id as user_id, p.id as post_id, title, body, created, author_id, username'
        ' FROM user u'
        ' LEFT JOIN post p ON p.author_id = u.id'
        ' WHERE u.username = %s',
        (username,)
    )
    posts = db.fetchall()
    print(posts)

    return render_template('/manage/profile.html', posts=posts)

@bp.route('/<string:username>/delete', methods=('GET', 'POST'))
@admin_user
def delete(username):
    script = 'SELECT username FROM user WHERE username = %s'

    db = get_db()
    db.execute(script, (username))

    # save the post into varible
    user = db.fetchone()

    # validate if the post exists
    if user is None:
        abort(404, f"User {username} doesn't exist.")
    
    else:
        
        script = "DELETE FROM user WHERE username = %s" 
        db.execute(script, (username,))
        g.connect.commit()

        return redirect(url_for('manage.menu'))


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

            db.execute(
            'SELECT id FROM user'
            ' WHERE username = %s',
            (username,)
            )
            user_id = db.fetchone()

            # insert the data of post
            db.execute(
                """INSERT INTO post (author_id, body, title)
                VALUES (%s, %s, %s)""", 
                (user_id['id'], body, title),
            )
            g.connect.commit() # save the change or the insert on db

            print(username, 'username muestra')

            return redirect(url_for('blog.index'))
        
        flash(error)
    return render_template('/blog/create.html')