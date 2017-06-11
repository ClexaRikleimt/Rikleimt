# encoding=utf-8
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_login import login_required

from .decorators import role_access
from .schemas import RoleSchema, UserSchema, PageSchema
from .models import db, Role, User, PageAccess


class RikleimtApi(Api):
    @staticmethod
    def check_permissions(view, view_args, view_kwargs, *args, **kwargs):
        raise NotImplementedError

    def init_app(self, app=None, blueprint=None):
        """Update flask application with our api

        :param Application app: a flask application
        :param Blueprint blueprint: existing blueprint to register the views on
        """
        if app is not None:
            self.app = app

        if blueprint is not None:
            self.blueprint = blueprint

        # for resource in self.resources:
        #     self.route(resource['resource'],
        #                resource['view'],
        #                *resource['urls'],
        #                url_rule_options=resource['url_rule_options'])


class RoleList(ResourceList):
    schema = RoleSchema
    data_layer = {
        'session': db.session,
        'model': Role
    }
    decorators = (login_required, role_access)  # decorate all methods with login_required and role_access


class RoleDetail(ResourceDetail):
    schema = RoleSchema
    data_layer = {
        'session': db.session,
        'model': Role
    }
    decorators = (login_required, role_access)  # decorate all methods with login_required and role_access


class RoleRelationship(ResourceRelationship):
    schema = RoleSchema
    data_layer = {
        'session': db.session,
        'model': Role
    }
    decorators = (login_required, role_access)  # decorate all methods with login_required and role_access


class UserList(ResourceList):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }
    decorators = (login_required, role_access)


class UserDetail(ResourceDetail):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }
    decorators = (login_required, role_access)


class UserRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }
    decorators = (login_required, role_access)


class PageList(ResourceList):
    schema = PageSchema
    data_layer = {
        'session': db.session,
        'model': PageAccess
    }
    decorators = (login_required, role_access)


class PageDetail(ResourceDetail):
    schema = PageSchema
    data_layer = {
        'session': db.session,
        'model': PageAccess
    }
    decorators = (login_required, role_access)


class PageRelationship(ResourceRelationship):
    schema = PageSchema
    data_layer = {
        'session': db.session,
        'model': PageAccess
    }
    decorators = (login_required, role_access)

