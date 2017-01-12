# encoding=utf-8
from wtforms import Form as FormInsecure
from wtforms import FormField, FieldList
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired
from flask import Markup

from rikleimt.models import Role
from rikleimt.blueprints.admin_pages.form_utils import (
    BS3StringField, BS3SelectField, BS3BooleanField, BS3PasswordField, BS3IntegerField, CKTextAreaField
)


# Helper forms
class RoleHelperForm(FormInsecure):
    role = BS3SelectField(label='Role: ', coerce=int, validators=[
        DataRequired(message='This is a required field.')
    ])

    def __init__(self, *args, **kwargs):
        # NOTE TO SELF/OTHERS: When copying this in the future, make sure to add the choices on view level too.
        # The choices here are to make sure the field will render, the set on view level is to make sure it validates.
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
        InputRequired(),
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


class CreateEpisodeForm(FlaskForm):
    episode_no = BS3IntegerField(label='Episode number', validators=[
        InputRequired()
    ])
    sfw = BS3BooleanField(label='Is the episode safe for work? ')
    n_sections = BS3IntegerField(label='How many sections, or scenes, are there in the episode? ', validators=[
        InputRequired()
    ], help_text="""
The episodes will be uploaded in the same set of scenes as they were written in. For example, the first episode,
the prologue includes, has 7 scenes: prologue, 1, 2, 3, 3B, 4, 5.
""")
    original_language = BS3SelectField(label='Language of the untranslated content: ', coerce=int, validators=[
        DataRequired()
    ], help_text="""
Until I can think of a better way to handle this, this field will be present here. The database storage does not know
that the default language of the content is English, so this is our way to connect fields below to the correct
language.
""")
    episode_name = BS3StringField(label='Name of the episode, if any: ')
    trigger_warnings = CKTextAreaField(label='Are there any trigger warnings the reader should be aware of? ')


class EditEpisodeForm(FlaskForm):
    episode_no = BS3IntegerField(label='Episode number', validators=[
        InputRequired()
    ])
    sfw = BS3BooleanField(label='Is the episode safe for work? ')
    n_sections = BS3IntegerField(label='How many sections, or scenes, are there in the episode? ', validators=[
        InputRequired()
    ], help_text="""
The episodes will be uploaded in the same set of scenes as they were written in. For example, the first episode,
the prologue includes, has 7 scenes: prologue, 1, 2, 3, 3B, 4, 5.
""")


class EditEpisodeTranslationForm(FlaskForm):
    # Episode number will be part of the URL, the page displaying this form will be loaded via a link on either the
    # episode index or on the details page of the specific episode.
    language = BS3SelectField(label='Language of the translation: ', coerce=int, validators=[
        DataRequired()
    ])  # On new translation: only display languages that are not translated yet, on existing only show db language
    episode_name = BS3StringField(label='Name of the episode, if any: ')
    trigger_warnings = CKTextAreaField(label='Are there any trigger warnings the reader should be aware of? ')


class EpisodeSectionForm(FlaskForm):
    # Episode number will be part of the URL, the page displaying this form will be loaded via a link on the
    # episode details page.
    # Same for the specific language
    section_no = BS3IntegerField(label='Section number: ', validators=[
        InputRequired()
    ], help_text="""
This needs to be a number. Say this is scene 3 of episode 1, the section number would be 4, because the prologue is
the first section. Then scene 3B would get the section number of 5, and scene 5 would become section number 7. This
number is used to put the scenes in the correct order when displaying the text.
""")
    section_text = CKTextAreaField(label='Finally, the text of the scene: ', validators=[
        InputRequired()
    ])
