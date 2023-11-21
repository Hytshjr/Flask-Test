from werkzeug.security import generate_password_hash
from flask import current_app, g
import sqlite3
import click


# Make the conecion with the code main
def init_app(app):
    print('init app realized')
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)


# Init the db
def init_db():
    # receive the connection of sqlite3
    db = get_db()

    # clear the existing data and create new tables
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Call Init db with "flask --app app init-db" in terminal
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


# Add users on db with "flask --app app user-db" in terminal
@click.command('user-db')
def add_user_command():
    db = get_db()

    user = input('Introduce un usuario: ')
    rol = input('Introduce un rol: ')
    password = input('Introduce una contraseña: ')

    # insert the data and the password as hash
    db.execute(
        """INSERT INTO user (username, rol, password)
        VALUES (?, ?, ?)""", 
        (user, rol,generate_password_hash(password)),
    )
    db.commit() # save the change or the insert on db
    click.echo('User add on the database.')


# Give the object that saves the connection from sql
def get_db():
    print('get_db')
    # make the connection

    if 'db' not in g:
        g.db = sqlite3.connect(
            #DATABASE is the path
            current_app.config['DATABASE'], 
            # detect format datatime or others
            detect_types=sqlite3.PARSE_DECLTYPES 
        )
        # set that give tha data as dictionary
        g.db.row_factory = sqlite3.Row

    click.echo('Connection alright!')
    return g.db
    

# Closed the connection 
def close_db(e=None):
    print('Close db')
    # such a list, replace the value for None
    db = g.pop('db', None)

    # verify that is None if don't is, just close the connection
    if db is not None:
        db.close()