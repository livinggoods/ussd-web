from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from config import config
import flask_excel as excel

# initialize flask extensions
# note, extensions are initalized with no Flask app instance because
# application factor is being used
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
admin = Admin()

login_manager = LoginManager()
login_manager.session_protection = 'strong'  # use strong session protection
login_manager.login_view = 'auth.login'  # set the endpoint for login page


def create_app(config_name):
    """
    Flask Application Factory that takes configuration settings and returns
    a Flask application.
    """
    # initalize instance of Flask application
    app = Flask(__name__)

    # import configuration settings into Flask application instance
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # initialize Flask extensions
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    excel.init_excel(app)
    admin = Admin(app, name='Admin', template_mode='bootstrap3')
    login_manager.init_app(app)

    ## Add admin
    from admins import UssdMessagesAdmin, UsersAdmin
    admin.add_view(UssdMessagesAdmin(db.session))
    admin.add_view(UsersAdmin(db.session))
    
    
    # redirect all http requests to https
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    # register 'main' blueprint with Flask application
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # register 'auth' blueprint with Flask application
    from .auth import auth as auth_blueprint
    # the 'url_prefix' parameter means all routes defined in the blueprint will
    # be registered with the prefix '/auth' (e.g., '/auth/login')
    app.register_blueprint(auth_blueprint, url_prefix='/user/auth')

    # register 'api' blueprint with Flask application
    from .api import api as api_blueprint
    # the 'url_prefix' parameter means all routes defined in the blueprint will
    # be registered with the prefix '/_api' (e.g., '/_api/relationships')
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
