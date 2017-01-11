# encoding=utf-8
from wtforms import Form as FormInsecure
from wtforms import FormField, FieldList
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from flask import Markup

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


class LanguageForm(FlaskForm):
    name = BS3StringField(label='Language name: ', validators=[
        DataRequired(message='This is a required field.')
    ])
    locale = BS3StringField(label='Locale code: ', validators=[
        DataRequired(message='This is a required field.')
    ], help_text=Markup("""
The `locale code`, or `language code` is a shortened form of the language name, following the locale syntax. It can
appear in 3 different forms: <br />
<ol>
<li>`en` : A 2 letter lowercase language identifier, using a ISO 639-1 language identifier</li>
<li>`pt_BR` : A 2 letter lowercase language identifier, followed by an underscore and a 2 letter uppercase
country identifier. The lowercase part uses ISO 639-1 and the uppercase part is a ISO 3166 language name.</li>
<li>`ru_UA@cyrillic` : This form will seldom be used. This uses the 2nd format, but ends with '@variant', where
variant is a (lowercase) description (for example script designator). This way, you can also have a language with
locale code `ru_UA@latin` for Russian spoken in Ukraine that uses the latin script.
</ol>
See <a href="https://www.gnu.org/software/gettext/manual/html_node/Usual-Language-Codes.html" target="_blank">
language code</a> for the lowercase language identifiers and for the
<a href="https://www.gnu.org/software/gettext/manual/html_node/Country-Codes.html" target="_blank">uppercase country
identifiers.</a>
"""))
