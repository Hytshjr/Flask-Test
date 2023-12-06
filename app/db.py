from flask import g
from decouple import config
import pymysql


# Acces to environment variable from .env
DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')


# Make the conecion with the code main
def init_app(app):
    print('init app realized')
    app.teardown_appcontext(close_db)


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