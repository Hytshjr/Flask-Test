from flask import Flask
import os

# create the app
def create_app():
    # set the object
    print('set app')
    app = Flask(__name__, instance_relative_config=True)

    # set the configuration
    print('set configuration')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

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