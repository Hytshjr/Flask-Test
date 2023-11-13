from flask import Blueprint, render_template, g, request, session
from flask import redirect, flash, url_for
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

    return render_template('manage/menu.html')
