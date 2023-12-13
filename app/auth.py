from flask import Blueprint, render_template, g, request, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, session
from app.db import get_db
import functools
import pymysql

bp = Blueprint('auth', __name__, url_prefix='/auth')

#  If is already logged redirect index
def logged_checking(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_id'] != None:
            # user loged, redirection on index
            return redirect(url_for('blog.index'))
        return view(*args, **kwargs)
    return wrapped_view

# If not is logged redirect login
def logged_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if session['user_id'] == None:
            # user don't loged, redirection on login
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view


# Recieve the data of user
def request_revify():
    if request.method == 'POST':
        # receive the values
        username = request.form['username']
        password = request.form['password']

        error = 'pass'

        # verify that not is empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        return error, username, password
    
    else:
        return None, None, None


# Verification if login is already
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id') # give the id in int
    script = 'SELECT username FROM user WHERE id = %s'

    # validate the id exists
    try:
        db = get_db()
        db.execute(script, (user_id,)) # give the username in str
        g.user = db.fetchone()['username']

    except:
        session['user_id'] = None
        session['user_rol'] = None
        g.user = None


@bp.route('/register', methods=('GET', 'POST'))
@logged_checking
def register():
    error, username, password = request_revify()

    if error == 'pass':
        # recieve the object db connect
        db = get_db()

        # set the rol default
        rol = 'user'

        # execute the query and insert user credential
        try:
            sql = """INSERT INTO user 
                    (username, rol, password) 
                    VALUES (%s, %s, %s)"""
            
            # insert the data and the password as hash
            db.execute(sql, 
                    (username, rol,generate_password_hash(password))
                    )
            g.connect.commit() # save the change or the insert on db
        
        except pymysql.IntegrityError: # error of username duplicate
            error = f"User {username} is already registered."

        else:
            return redirect(url_for("auth.login"))
        
    if error is None:
        pass

    else:
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
@logged_checking
def login():
    error, username, password = request_revify()

    # validate the request
    if error == 'pass':

        # recieve the object db connect
        db = get_db()

        sql = """SELECT * FROM user WHERE username = %s"""

        # search the username if that exists
        db.execute(sql, (username,))
        credentials = db.fetchone() 

        # check if don't find someuser
        if not credentials:
            error = ('The username is incorrect.')

        # validate the password
        elif not check_password_hash(credentials['password'], password):
            error = ('Your password is incorrect.')

        # if the user and password is true move on
        if error == 'pass':
            session.clear() # clean the data into variable
            session['user_id'] = credentials['id'] # give id of db
            session['user_rol'] = credentials['rol'] # give id of db
            g.user = credentials['username']
            
            return redirect(url_for('blog.index'))
    
    if error is None:
        pass

    else:
        flash(error)
        
    return render_template('/auth/login.html')


@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session['user_id'] = None
    session['user_rol'] = None
    g.user = None # delete the username

    return redirect(url_for('blog.index'))









