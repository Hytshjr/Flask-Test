from flask import Blueprint, render_template, g, request, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, flash, session
from functools import wraps
from app.db import get_db
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Redirection if is already logged
def logged_checking(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_id'] != None:
            # user loged, redirection on index
            return redirect(url_for('blog.index'))
        return view(*args, **kwargs)
    return wrapped_view

# Redirection if not is logged
def logged_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_id'] == None:
            # user don't loged, redirection on login
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view


# Verification if login is already
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id') # give the id in int

    # validate the id exists
    if user_id is None:
        session['user_id'] = None
        g.user = None

    else:
        try:
            g.user = get_db().execute(
                'SELECT username FROM user WHERE id = ?', (user_id,)
            ).fetchone()[0] # give the username in str

        except:
            session['user_id'] = None
            g.user = None



@bp.route('/register', methods=('GET', 'POST'))
@logged_checking
def register():
    error, username, password = request_revify()

    if error is None:
        # recieve the object db connect
        db = get_db()
        error = None

        # set the rol default
        rol = 'user'

        try:
            # insert the data and the password as hash
            db.execute(
                """INSERT INTO user (username, rol, password)
                VALUES (?, ?, ?)""", 
                (username, rol,generate_password_hash(password)),
            )
            db.commit() # save the change or the insert on db
        
        except db.IntegrityError: # error of username duplicate
            error = f"User {username} is already registered."
            flash(error)

        else:
            return redirect(url_for("auth.login"))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
@logged_checking
def login():
    error, username, password = request_revify()

    # validate the request
    if error == None:

        # recieve the object db connect
        db = get_db()

        # search the username if that exists
        credentials = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchall()
        
        # check if don't find someuser
        if not bool(credentials):
            error = (f'The user {username} not is registred.')

        # validate the password
        elif not check_password_hash(credentials[0][3], password):
            error = ('Your password is incorrect.')

        # if the user and password is true move on
        if error is None:
            # session.clear() # clean the data into variable
            session['user_id'] = credentials[0][0] # give id of db
            session['user_rol'] = credentials[0][2] # give id of db
            
            return redirect(url_for('blog.index'))
        
        flash(error)
        
    return render_template('/auth/login.html')


@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    if session['user_id'] != None:
        session['user_rol'] = None # delete the rol
        session['user_id'] = None # delete the id
        g.user = None # delete the username

    return redirect(url_for('blog.index'))


def request_revify():
    if request.method == 'POST':
        # receive the values
        username = request.form['username']
        password = request.form['password']

        error = None

        # verify that not is empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'


        return error, username, password
    
    else:
        return 'wait', None, None





