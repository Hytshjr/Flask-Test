from flask import Blueprint, render_template, g, request, session
from flask import redirect, flash, url_for
from .db import get_db
import functools

bp = Blueprint('manage', __name__, url_prefix='/manage')

def admin_user(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_rol'] != 'admin':
            return redirect(url_for('blog.index'))
        return view(*args, **kwargs)
    return wrapped_view

@bp.route('/menu')
@admin_user
def manu():
    db = get_db()
    
    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()

    print(users[0][0])

    return render_template('manage/menu.html', posts=users)


@bp.route('/<str:username>/orfile', methods=('GET', 'POST'))
@admin_user
def update(username):

    # if posts['author_id'] == session['user_id'] or session['user_rol'] == 'admin':
    #     pass