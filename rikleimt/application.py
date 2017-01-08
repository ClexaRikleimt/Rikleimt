# encoding=utf-8
from flask import Flask, request

from flask_login import LoginManager
from flask_babel import Babel

login_manager = LoginManager()
babel = Babel()


@babel.localeselector
def get_locale():
    # TODO: Add code to resolve language changes later on [Arlena]

    # TODO: Add the languages for the frontend to this list. This will only be used for static translations [Arlena]
    return request.accept_languages.best_match(['en'])


def create_app():
    app = Flask(__name__)

    # Configure the app
    app.config.from_object('rikleimt.config')

    from rikleimt.models import db
    db.init_app(app)

    from rikleimt.assets import assets
    assets.init_app(app)
    with app.app_context():
        assets.url = app.static_url_path

    login_manager.init_app(app)

    babel.init_app(app)

    return app
