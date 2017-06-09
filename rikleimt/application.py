# encoding=utf-8
from flask import Flask, request

from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask_bcrypt import Bcrypt

from .utils import WikiArticleConverter

db_migrate = Migrate()
login_manager = LoginManager()
babel = Babel()
bcrypt_ = Bcrypt()


@babel.localeselector
def get_locale():
    # TODO: Add code to resolve language changes later on [Arlena]

    # TODO: Add the languages for the frontend to this list. This will only be used for static translations [Arlena]
    return request.accept_languages.best_match(['en'])


def create_app():
    app = Flask(__name__)

    # Configure the app
    app.config.from_object('rikleimt.config')

    from .models import db
    db.init_app(app)
    db_migrate.init_app(app, db)

    from .assets import assets
    assets.init_app(app)
    with app.app_context():
        assets.url = app.static_url_path

    login_manager.init_app(app)

    bcrypt_.init_app(app)

    babel.init_app(app)

    # Register processors
    app.url_map.converters['article'] = WikiArticleConverter

    # Register blueprints
    from .blueprints.api import api_bp
    from .blueprints.admin_pages import admin_pages_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_pages_bp, url_prefix='/admin')

    return app
