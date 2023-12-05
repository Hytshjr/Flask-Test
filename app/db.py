from werkzeug.security import generate_password_hash
from flask import current_app, g
from decouple import config
import pymysql
import click


# Acces to environment variable from .env
DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')


# Make the conecion with the code main
def init_app(app):
    print('init app realized')
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)


# Init the db
def init_db():
    # receive the connection of mysql
    db = get_db()

    try:
        with db as cursor:
            with open('app\schema.sql', 'r') as script_file:
                script = script_file.read()
                print(script,'this file')

            cursor.execute(script)
        
        g.connect.commit()

    except():
        pass


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

    # make the connection
    if 'db' not in g:
        g.connect = pymysql.connect(
            host    = DB_HOST, 
            user    = DB_USER, 
            passwd  = DB_PASSWORD, 
            db      = DB_NAME
            )
        
        # pymysql.cursors.DictCursor save the query as dict
        g.db = g.connect.cursor(pymysql.cursors.DictCursor)
    return g.db
    

# Closed the connection 
def close_db(e=None):
    # such a list, replace the value for None
    connect = g.pop('connect', None)

    # verify that is None if don't is, just close the connection
    if connect is not None:
        connect.close()