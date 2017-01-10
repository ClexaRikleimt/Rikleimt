# encoding=utf-8
from wtforms import Form as FormInsecure
from wtforms import FormField, FieldList
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired

from rikleimt.models import Role
from rikleimt.blueprints.admin_pages.form_utils import (
    BS3StringField, BS3SelectField, BS3BooleanField, BS3PasswordField, CKTextAreaField
)


# Helper forms
class RoleHelperForm(FormInsecure):
    role = BS3SelectField(label='Role: ', coerce=int, validators=[
        DataRequired(message='This is a required field')
    ])

    def __init__(self, *args, **kwargs):
        # NOTE TO SELF/OTHERS: When copying this in the future, make sure to add the choices on view level too
        roles = Role.query.order_by('name').all()
        self.role.choices = [(r.id, r.name) for r in roles]

        super(RoleHelperForm, self).__init__(*args, **kwargs)


# Forms
class LoginForm(FlaskForm):
    email = BS3StringField(label='Email address: ', validators=[
        DataRequired(message='This is a required field.')
    ])
    password = BS3PasswordField(label='Password: ', validators=[
        DataRequired(message='This is a required field.')
    ])
    remember = BS3BooleanField(label='Remember me? ')


class KepaWochaUserFormCreate(FlaskForm):
    email = BS3StringField(label='Email address: ', validators=[
        DataRequired(message='This is a required field.'),
        Email(message='This is not a valid email address.')
    ])
    password = BS3PasswordField(label='Password: ', validators=[
        InputRequired,
        EqualTo('confirm_password', 'Passwords must match')
    ])
    confirm_password = BS3PasswordField(label='Confirm password: ')
    role = BS3SelectField(label="User's role: ", coerce=int)
    activated = BS3BooleanField(label='Activate user? ')


class KepaWochaUserFormEdit(FlaskForm):
    email = BS3StringField(label='Email address: ', validators=[
        DataRequired(message='This is a required field.')
    ])
    role = BS3SelectField(label="User's role: ", coerce=int)
    activated = BS3BooleanField(label='Activate user? ')


class RoleForm(FlaskForm):
    name = BS3StringField(label='Role name: ', validators=[
        DataRequired(message='This is a required field.')
    ])


class PageAccessForm(FlaskForm):
    page_name = BS3StringField(label='Page name: ', validators=[
        DataRequired(message='This is a required field.')
    ])
    page_endpoint = BS3StringField(label='Page endpoint: ', validators=[
        DataRequired(message='This is a required field.')
    ], help_text="""
Do not edit this field if you don't know how it works. The administrative part of the site can break if a wrong value
is entered here. This field is formatted as `a.b`, where `a` is the name of the blueprint where the page
lives and `b` is the endpoint of the page, as is specified in the source code. For example,
the index page where you are redirected after you log in, has the following page endpoint: `admin_pages.index`.
""")
    in_menu = BS3BooleanField(label='Display in menu? ')
    is_administrative = BS3BooleanField(label='Is this an administrative page? ', help_text="""
An administrative page is a page that is only 'helping' on this part of the site. The pages where you edit the
book are not administrative, but a page where you edit which users have access to the site is.
""")
    roles = FieldList(FormField(RoleHelperForm), 'Roles: ', validators=[
        DataRequired(message='This is a required field')
    ], min_entries=1)
