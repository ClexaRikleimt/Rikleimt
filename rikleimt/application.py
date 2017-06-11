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

from rikleimt.api import RikleimtApi
api = RikleimtApi()


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

    api.init_app(app)
    setup_api(api)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_pages_bp, url_prefix='/admin')

    return app


def setup_api(api_):
    from .api import (
        RoleList, RoleDetail, RoleRelationship,
        UserList, UserDetail, UserRelationship,
        PageList, PageDetail, PageRelationship
    )

    api_.route(RoleList, 'role_list', '/roles')
    api_.route(RoleDetail, 'role_detail', '/roles/<int:id>')
    api_.route(RoleRelationship, 'role_users', '/roles/<int:id>/relationships/users')
    api_.route(RoleRelationship, 'role_pages', '/roles/<int:id>/relationships/pages')

    api_.route(UserList, 'user_list', '/users')
    api_.route(UserDetail, 'user_detail', '/users/<int:id>')
    api_.route(UserRelationship, 'user_role', '/users/<int:id>/relationships/role')

    api_.route(PageList, 'page_list', '/pages')
    api_.route(PageDetail, 'page_detail', '/pages/<int:id>')
    api_.route(PageRelationship, 'page_roles', '/pages/<int:id>/relationships/roles')
