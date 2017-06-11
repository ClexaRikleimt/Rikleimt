# encoding=utf-8
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields


class RoleSchema(Schema):
    class Meta:
        type_ = 'role'
        self_view = 'role_detail'
        self_view_kwargs = {
            'id': '<id>'
        }
        self_view_many = 'role_list'

    id = fields.Str(dump_only=True)  # write-only
    name = fields.Str(required=True)

    users = Relationship(
        self_view='role_users',
        self_view_kwargs={
            'id': '<id>'
        },
        related_view='user_list',
        related_view_kwargs={
            'id': '<id>'
        },
        many=True,
        schema='UserSchema',
        type_='user'
    )
    pages = Relationship(
        self_view='role_pages',
        self_view_kwargs={
            'id': '<id>'
        },
        related_view='page_list',
        related_view_kwargs={
            'id': '<id>'
        },
        many=True,
        schema='PageSchema',
        type_='page'
    )


class UserSchema(Schema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {
            'id': '<id>'
        }
        self_view_many = 'user_list'

    id = fields.Str(dump_only=True)  # write-only
    email = fields.Email(required=True)
    activated = fields.Boolean(required=True, default=False)

    role = Relationship(
        self_view='user_role',
        self_view_kwargs={
            'id': '<id>'
        },
        related_view='role_list',
        related_view_kwargs={
            'id': '<id>'
        },
        schema='RoleSchema',
        type_='role'
    )


class PageSchema(Schema):
    class Meta:
        type_ = 'page'
        self_view = 'page_detail'
        self_view_kwargs = {
            'id': '<id>'
        }
        self_view_many = 'page_list'

    id = fields.Str(dump_only=True)  # write-only
    name = fields.Str(required=True)
    endpoint = fields.Str(required=True)

    roles = Relationship(
        self_view='page_roles',
        self_view_kwargs={
            'id': '<id>'
        },
        related_view='role_list',
        related_view_kwargs={
            'id': '<id>'
        },
        many=True,
        schema='RoleSchema',
        type_='role'
    )
