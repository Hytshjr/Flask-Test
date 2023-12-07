from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from decouple import config
from flask import g
import pymysql


# Acces to environment variable from .env
DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')


# Make the conecion with the code main
def init_app(app):
    create_db()
    create_table(app)
    app.teardown_appcontext(close_db)

    print('Init app realized')


# Create a DATABASE
def create_db():
    # connect 
    connection = pymysql.connect(host=DB_HOST,
                                user=DB_USER,
                                password=DB_PASSWORD)  

    # recieve a cursor
    cursor = connection.cursor()

    try:
        # create the BD
        cursor.execute(f"CREATE DATABASE {DB_NAME}")

        # closed connection
        connection.close()
    
    except:
        print('The DB is already create.')


# Create a tables
def create_table(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}"

    db = SQLAlchemy(app) # init SQLAlchemy

    # set the table user
    class User(db.Model):
        id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
        username    = db.Column(db.String(80), nullable=False, unique=True)
        rol         = db.Column(db.String(80), nullable=False)
        password    = db.Column(db.String(255), nullable=False)

    # set the table post
    class Post(db.Model):
        id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
        author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        created     = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
        title       = db.Column(db.String(120), nullable=False)
        body        = db.Column(db.Text, nullable=False)

    try:
        with app.app_context():  # init context
            # create the migration initial
            db.create_all()

    except Exception as e:
        print(f'Error creating tables: {e}')

    


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
    
    return connect