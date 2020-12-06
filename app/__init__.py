from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

login_manager = LoginManager()
# this sets a view that the login manager redirects to when an
# anonymous user tries to access a protected view
login_manager.login_view = 'auth.login'
mail = Mail()
migrate = Migrate()


# create naming convention for Alembic migrations
# as per Flask docs: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#using-custom-metadata-and-naming-conventions
# with an update to "ck": https://github.com/sqlalchemy/sqlalchemy/issues/3345
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    print('just configured app')
    print(app)

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # set render_as_batch=True to fix sqlite migration issues
    # as per Miguel: https://youtu.be/wpRVZFwsD70
    migrate.init_app(app, db, render_as_batch=True)
    
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)


    from . import main
    app.register_blueprint(main.bp)
    # urls inside of blueprints are typically given their own namespace,
    # but in this case we want this to be the default
    app.add_url_rule('/', endpoint='index')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app