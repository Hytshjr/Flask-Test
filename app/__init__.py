from flask import Flask
from decouple import config
import os

APP_PASSWORD = config('APP_PASSWORD')


# create the app
def create_app(test_config=None):
    # set the object
    app = Flask(__name__, instance_relative_config=True)
    app.run(host="0.0.0.0", port=80)

    # set the configuration
    app.config.from_mapping(
        SECRET_KEY=APP_PASSWORD,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)

    except OSError:
        pass

    print('Import db')
    from . import db
    db.init_app(app)

    print('Import auth')
    from . import auth
    app.register_blueprint(auth.bp)

    print('Import blog')
    from . import blog
    app.register_blueprint(blog.bp)

    print('Import manage')
    from . import manage
    app.register_blueprint(manage.bp)


    return app
