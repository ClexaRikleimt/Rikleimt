# encoding=utf-8
import datetime

from flask import render_template, url_for, flash, request, redirect
from flask.views import View, MethodView
from flask_login import login_required, login_user, logout_user, current_user

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from rikleimt.blueprints.admin_pages.forms import (
    LoginForm, Rik3UserFormCreate, Rik3UserFormEdit, RoleForm, PageAccessForm, RoleHelperForm, LanguageForm,
    CreateEpisodeForm, EditEpisodeForm, EditEpisodeTranslationForm, EpisodeSectionForm
)
from rikleimt.blueprints.admin_pages.exceptions import IncompleteEpisodeSectionException
from rikleimt.decorators import role_access
from rikleimt.models import (
    db,
    # Models:
    User, Role, PageAccess, Language, Episode, EpisodeDetails, EpisodeSection, EpisodeRevision, EpisodeText,
    # Exceptions:
    RevisionNotFoundException
)


# TODO: Improve error messages on rollback actions


class Login(View):
    endpoint = 'login'

    def dispatch_request(self):
        error_message = 'This combination of email and password was not found.'

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter(User.email == form.email.data).first()
            if user is None:
                # User is not known, flash message and return
                flash(error_message, 'error')
                return render_template('admin_pages/login.html', form=form)
            if user.validate_password(form.password.data):
                # Valid login
                if not login_user(user, form.remember.data):
                    flash('This account is not yet or no longer allowed to log in. Contact kepa-wocha with questions.',
                          'error')
                    return render_template('admin_pages/login.html', form=form)

                next_ = request.args.get('next')
                # TODO: validate `next_` (now vulnerable for open redirects) [Arlena]
                return redirect(next_ or url_for('.index'))
            else:
                flash(error_message, 'error')
                render_template('admin_pages/login.html', form=form)
        return render_template('admin_pages/login.html', form=form)


class Logout(View):
    endpoint = 'logout'
    decorators = [login_required]

    def dispatch_request(self):
        logout_user()
        return redirect(url_for('.{0}'.format(Login.endpoint)))


class Index(View):
    endpoint = 'index'
    decorators = [login_required]

    def dispatch_request(self):
        return render_template('admin_pages/index.html')


class Rik3Users(View):
    endpoint = 'rik3_users'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        users = User.query.all()

        return render_template('admin_pages/rik3_users.html', users=users)


class Rik3EditUser(MethodView):
    # TODO: Optimise (DRY) [Arlena]
    endpoint = 'rik3_edit_user'
    decorators = [login_required, role_access]

    @staticmethod
    def _prepare_form(form):
        form.role.choices = [(r.id, r.name) for r in Role.query.all()]
        return form

    def get(self, user_id):
        if user_id == -1:
            # New user
            form = self._prepare_form(Rik3UserFormCreate())
        else:
            user = User.query.filter(User.id == user_id).first()
            if not user:
                flash('The user that was selected to edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(Rik3Users.endpoint)))

            form = self._prepare_form(Rik3UserFormEdit())

            form.email.data = user.email
            form.role.data = user.role_id
            form.activated.data = user.activated

        return render_template('admin_pages/rik3_user_edit.html', form=form, user_id=user_id)

    def post(self, user_id):
        if user_id == -1:
            # New user
            form = self._prepare_form(Rik3UserFormCreate())
        else:
            user = User.query.filter(User.id == user_id).first()
            if not user:
                flash('The user that was selected to edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(Rik3Users.endpoint)))

            form = self._prepare_form(Rik3UserFormEdit())

        if form.validate_on_submit():
            if user_id == -1:
                user = User(form.email.data, User.hash_password(form.password.data), form.role.data,
                            form.activated.data)
                db.session.add(user)
                try:
                    db.session.commit()
                except IntegrityError as exception:
                    db.session.rollback()
                    # TODO: testing [Arlena]
                    flash('Failed to create the user. Technical data: {0}'.format(exception), 'error')
                    return render_template('admin_pages/rik3_user_edit.html', form=form, user_id=user_id)
                else:
                    flash('Successfully created the new user.', 'info')
                    return redirect(url_for('.{0}'.format(Rik3Users.endpoint)))
            else:
                user = User.query.filter(User.id == user_id).first()
                user.email = form.email.data
                user.role_id = form.role.data
                user.activated = form.activated.data

                try:
                    db.session.commit()
                except IntegrityError as exception:
                    db.session.rollback()
                    # TODO: testing [Arlena]
                    flash('Failed to edit the user. Technical data: {0}'.format(exception), 'error')
                    return render_template('admin_pages/rik3_user_edit.html', form=form, user_id=user_id)
                else:
                    flash('Successfully edited the user.', 'info')
                    return redirect(url_for('.{0}'.format(Rik3Users.endpoint)))

        return render_template('admin_pages/rik3_user_edit.html', form=form, user_id=user_id)


class Roles(View):
    endpoint = 'roles'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        roles = Role.query.all()

        return render_template('admin_pages/roles.html', roles=roles)


class EditRole(MethodView):
    endpoint = 'edit_role'
    decorators = [login_required, role_access]

    def get(self, role_id):
        form = RoleForm()

        if role_id == -1:
            # New role
            pass
        else:
            role = Role.query.filter(Role.id == role_id).first()
            if not role:
                flash('The role that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(Roles.endpoint)))

            form.name.data = role.name

        return render_template('admin_pages/roles_edit.html', form=form, role_id=role_id)

    def post(self, role_id):
        form = RoleForm()

        if form.validate_on_submit():
            if role_id == -1:
                # New role
                role = Role(form.name.data)
                db.session.add(role)
                try:
                    db.session.commit()
                except IntegrityError as exception:
                    db.session.rollback()
                    # TODO: testing [Arlena]
                    flash('Failed to create the new role. Technical data: {0}'.format(exception), 'error')
                    return render_template('admin_pages/roles_edit.html', form=form, role_id=role_id)
                else:
                    flash('Successfully created the role.', 'info')
                    return redirect(url_for('.{0}'.format(Roles.endpoint)))
            else:
                role = Role.query.filter(Role.id == role_id).first()
                if not role:
                    flash('The role that was selected for edit does not exist.', 'error')
                    return redirect(url_for('.{0}'.format(Roles.endpoint)))

                role.name = form.name.data
                try:
                    db.session.commit()
                except IntegrityError as exception:
                    # TODO: testing [Arlena]
                    db.session.rollback()
                    flash('Failed to edit the role. Technical data: {0}'.format(exception), 'error')
                    return render_template('admin_pages/roles_edit.html', form=form, role_id=role_id)
                else:
                    flash('Successfully edited the role.', 'info')
                    return redirect(url_for('.{0}'.format(Roles.endpoint)))

        return render_template('admin_pages/roles_edit.html', form=form, role_id=role_id)


class AdminPages(View):
    endpoint = 'admin_pages'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        admin_pages = PageAccess.query.all()

        return render_template('admin_pages/admin_pages.html', admin_pages=admin_pages)


class EditAdminPage(MethodView):
    endpoint = 'edit_admin_page'
    decorators = [login_required, role_access]
    min_roles = 1

    def get(self, page_id):
        form = PageAccessForm()

        roles = Role.query.order_by('name').all()
        role_choices = [(r.id, r.name) for r in roles]

        if page_id == -1:
            # New admin page, prepare form with default entries
            for entry in form.roles.entries:
                entry.role.choices = role_choices
        else:
            # Existing admin page, pull info from db
            res = PageAccess.query.filter(PageAccess.id == page_id).first()
            if not res:
                flash('The page that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(AdminPages.endpoint)))

            form.page_name.data = res.name
            form.page_endpoint.data = res.endpoint
            form.in_menu.data = res.in_menu
            form.is_administrative.data = res.is_administrative

            # Remove empty entries of 'roles'
            for _ in range(0, form.roles.min_entries):
                form.roles.pop_entry()

            for role in res.roles:
                helper_form = RoleHelperForm()
                helper_form.role = role.id
                form.roles.append_entry(helper_form)

            for entry in form.roles.entries:
                entry.role.choices = role_choices
                entry.role.default = entry.role.data

        return render_template('admin_pages/admin_pages_edit.html', form=form, page_id=page_id,
                               min_roles=self.min_roles)

    def post(self, page_id):
        form = PageAccessForm()

        roles = Role.query.order_by('name').all()
        role_choices = [(r.id, r.name) for r in roles]

        for entry in form.roles.entries:
            entry.role.choices = role_choices

        if not form.validate_on_submit():
            return render_template('admin_pages/admin_pages_edit.html', form=form, page_id=page_id,
                                   min_roles=self.min_roles)

        if page_id == -1:
            # New admin page
            page = PageAccess(form.page_name.data, form.page_endpoint.data, form.in_menu.data,
                              form.is_administrative.data)
            for entry in form.roles.entries:
                role = Role.query.filter(Role.id == entry.role.data).first()
                if role not in page.roles:
                    page.roles.append(role)

            db.session.add(page)

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: Testing [Arlena]
                flash('Failed to create a new administrative page. Tech data: {0}'.format(exception), 'error')
                return render_template('admin_pages/admin_pages_edit.html', form=form, page_id=page_id,
                                       min_roles=self.min_roles)
            else:
                flash('Successfully created {0!r}'.format(form.page_name.data), 'info')
                return redirect(url_for('.{0}'.format(AdminPages.endpoint)))
        else:
            # Existing page, pull info from db
            res = PageAccess.query.filter(PageAccess.id == page_id).first()
            if not res:
                flash('The page that was selected for edit does not exist.', 'error')
                return render_template('admin_pages/admin_pages_edit.html', form=form, page_id=page_id,
                                       min_roles=self.min_roles)

            page = PageAccess.query.filter(PageAccess.id == page_id).first()
            page.name = form.page_name.data
            page.endpoint = form.page_endpoint.data
            page.in_menu = form.in_menu.data
            page.is_administrative = form.is_administrative.data

            form_roles = set()

            for entry in form.roles.entries:
                role = Role.query.filter(Role.id == entry.role.data).first()
                form_roles.add(role)

            for role in page.roles:
                if role not in form_roles:
                    # Existed in this page before, but was removed.
                    page.roles.remove(role)
                else:
                    # Already exist in this page
                    form_roles.remove(role)

            for role in form_roles:
                # Only roles that aren't already in the page.roles will now be listed here
                page.roles.append(role)

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to edit this administrative page. Tech data: {0}'.format(exception), 'error')
                return render_template('admin_pages/admin_pages_edit.html', form=form, page_id=page_id,
                                       min_roles=self.min_roles)
            else:
                flash('Successfully edited {0!r}'.format(form.page_name.data), 'info')
                return redirect(url_for('.{0}'.format(AdminPages.endpoint)))


class LanguagesIndex(View):
    endpoint = 'languages_index'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        languages = Language.query.order_by('name').all()

        return render_template('admin_pages/languages.html', languages=languages)


class EditLanguage(MethodView):
    endpoint = 'edit_language'
    decorators = [login_required, role_access]

    def get(self, language_id):
        form = LanguageForm()

        if language_id == -1:
            # New language
            pass
        else:
            # Pull info from db
            lang = Language.query.filter(Language.id == language_id).first()
            if not lang:
                flash('The language that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(LanguagesIndex.endpoint)))

            form.name.data = lang.name
            form.locale.data = lang.locale_code

        return render_template('admin_pages/languages_edit.html', form=form, language_id=language_id)

    def post(self, language_id):
        form = LanguageForm()

        if not form.validate_on_submit():
            return render_template('admin_pages/languages_edit.html', form=form, language_id=language_id)

        if language_id == -1:
            lang = Language(form.name.data, form.locale.data)
            db.session.add(lang)

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to create language {0!r}. Tech data: {1}'.format(form.name.data, exception), 'error')
                return render_template('admin_pages/languages_edit.html', form=form, language_id=language_id)
            else:
                flash('Successfully created language {0!r}'.format(form.name.data), 'info')
                return redirect(url_for('.{0}'.format(LanguagesIndex.endpoint)))
        else:
            lang = Language.query.filter(Language.id == language_id).first()
            if not lang:
                flash('The language that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(LanguagesIndex.endpoint)))

            lang.name = form.name.data
            lang.locale_code = form.locale.data

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to edit language {0!r}. Tech data: {1}'.format(form.name.data, exception), 'error')
                return render_template('admin_pages/languages_edit.html', form=form, language_id=language_id)
            else:
                flash('Successfully edited language {0!r}'.format(form.name.data), 'info')
                return redirect(url_for('.{0}'.format(LanguagesIndex.endpoint)))


# Welcome to the monster of code that is the handling of episodes and editing them. Please, make yourself a warm
# cup of coffee or tea before diving in. And comment on commits/slack with questions, as it is hard to
# understand for the author too... :/
class EpisodeIndex(View):
    """View that shows an index of all episodes"""
    endpoint = 'episode_index'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        episodes = Episode.query.all()

        # Better to do those db queries up front, than having to repeat them in the template
        episodes_languages = {}
        for episode in episodes:
            episodes_languages[episode.episode_no] = episode.languages_available_in

        return render_template('admin_pages/episodes_index.html', episodes=episodes,
                               episodes_languages=episodes_languages)


class EditEpisode(MethodView):
    """View that shows the form to edit static episode content"""
    endpoint = 'edit_episode'
    decorators = [login_required, role_access]

    def get(self, episode_no):
        if episode_no == -1:
            # New episode, show different form
            form = CreateEpisodeForm()
            form.original_language.choices = [(l.id, l.name) for l in Language.query.all()]
            # TODO: Intialise the form with total number of episodes + 1 as episode_no
        else:
            form = EditEpisodeForm()

            # Pull info from db
            episode = Episode.query.filter(Episode.episode_no == episode_no).first()
            if not episode:
                flash('The episode selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

            form.episode_no.data = episode.episode_no
            form.sfw.data = episode.sfw
            form.n_sections.data = episode.n_sections

        return render_template('admin_pages/edit_episode.html', form=form, episode_no=episode_no)

    def post(self, episode_no):
        if episode_no == -1:
            # New episode, show different form
            form = CreateEpisodeForm()
            form.original_language.choices = [(l.id, l.name) for l in Language.query.all()]
        else:
            form = EditEpisodeForm()

        if not form.validate_on_submit():
            return render_template('admin_pages/edit_episode.html', form=form, episode_no=episode_no)

        if episode_no == -1:
            episode = Episode(form.episode_no.data, form.sfw.data, form.n_sections.data)
            details = EpisodeDetails(form.original_language.data, form.episode_no.data,
                                     form.episode_name.data if form.episode_name.data is not '' else None,
                                     form.trigger_warnings.data if form.trigger_warnings.data is not '' else None)

            db.session.add(episode)
            db.session.add(details)

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to create the new episode {0}. Tech data: {1!r}'.format(form.episode_no.data, exception),
                      'error')
                return render_template('admin_pages/edit_episode.html', form=form, episode_no=episode_no)
            else:
                flash('Successfully created episode {0}'.format(form.episode_no.data), 'info')
                return redirect(url_for('.{0}'.format(EpisodeTranslationDetails.endpoint),
                                        episode_no=episode.episode_no, language_id=form.original_language.data))
        else:
            episode = Episode.query.filter(Episode.episode_no == episode_no).first()
            if not episode:
                flash('The episode selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

            episode.episode_no = form.episode_no.data
            episode.sfw = form.sfw.data
            episode.n_sections = form.sfw.data

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to edit this episode. Tech data: {0!r}'.format(exception), 'error')
                return render_template('admin_pages/edit_episode.html', form=form, episode_no=episode_no)
            else:
                flash('Successfully edited episode {0}'.format(form.episode_no.data), 'info')
                return redirect(url_for('.{0}'.format(EpisodeViewDetails.endpoint), episode_no=episode_no))


class EpisodeTranslationDetails(View):
    """View that shows information about a given 'translation' of an episode, including the sections."""
    endpoint = 'episode_translation_details'
    decorators = [login_required, role_access]

    def dispatch_request(self, episode_no, language_id):
        details = EpisodeDetails.query.filter(db.and_(
            EpisodeDetails.episode_no == episode_no, EpisodeDetails.language_id == language_id)
        ).first()
        if not details:
            flash('Translation of this episode was not found', 'error')
            return redirect(url_for('.{0}'.format(EpisodeViewDetails.endpoint), episode_no=episode_no))

        sections = EpisodeSection.query.filter(db.and_(
            EpisodeSection.episode_no == episode_no, EpisodeSection.language_id == language_id
        )).order_by(EpisodeSection.section_no).all()

        return render_template('admin_pages/episode_translation_details.html', details=details, sections=sections)


class EpisodeEditTranslation(MethodView):
    """View that shows the form to edit translatable episode content"""
    endpoint = 'edit_episode_translation'
    decorators = [login_required, role_access]

    def get(self, episode_no, language_id):
        episode = Episode.query.filter(Episode.episode_no == episode_no).first()
        if not episode:
            flash('The episode that was selected for edit does not exist.', 'error')
            return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

        form = EditEpisodeTranslationForm()

        if language_id == -1:
            # New translation, prepare form with allowed languages
            form.language.choices = [(id_, name) for id_, name in episode.languages_not_translated_to.items()]
        else:
            # Existing, pull info from db, put set the language selection to only include the current one
            details = EpisodeDetails.query.filter(db.and_(
                EpisodeDetails.episode_no == episode_no, EpisodeDetails.language_id == language_id
            )).first()
            if not details:
                flash('The translation that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(EpisodeViewDetails.endpoint), episode_no=episode_no))

            form.language.choices = [(language_id, details.language.name)]
            form.language.data = language_id
            form.episode_name.data = details.title
            form.trigger_warnings.data = details.warnings

        return render_template('admin_pages/edit_episode_translation.html', form=form, episode_no=episode_no,
                               language_id=language_id)

    def post(self, episode_no, language_id):
        episode = Episode.query.filter(Episode.episode_no == episode_no).first()
        if not episode:
            flash('The episode that was selected for edit does not exist.', 'error')
            return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

        form = EditEpisodeTranslationForm()

        if language_id == -1:
            # New translation, add allowed languages to the form for validation
            form.language.choices = [(id_, name) for id_, name in episode.languages_not_translated_to.items()]
        else:
            # Existing, put the language selection to only include the current one
            language = Language.query.filter(Language.id == language_id).first()
            if not language:
                flash('The language that was selected to translate to does not exist.', 'error')

            form.language.choices = [(language_id, language.name)]

        if not form.validate_on_submit():
            return render_template('admin_pages/edit_episode_translation.html', form=form, episode_no=episode_no,
                                   language_id=language_id)
        if language_id == -1:
            # Add translation to database
            translation = EpisodeDetails(form.language.data, episode_no, form.episode_name.data,
                                         form.trigger_warnings.data)
            db.session.add(translation)

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to create a new translation of episode {0}. Tech data: {0!r}'.format(
                    episode_no, exception
                ), 'error')
                return render_template('admin_pages/edit_episode_translation.html', form=form, episode_no=episode_no,
                                       language_id=language_id)
            else:
                flash('Successfully created a new translation in {0} of episode {1}'.format(
                    translation.language.name, episode_no
                ), 'info')
                return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))
        else:
            details = EpisodeDetails.query.filter(db.and_(
                EpisodeDetails.episode_no == episode_no, EpisodeDetails.language_id == language_id
            )).first()
            if not details:
                flash('The translation that was selected for edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

            # The language part has become static on editing, so we won't have to send a change for that to the db
            details.title = form.episode_name.data
            details.warnings = form.trigger_warnings.data

            try:
                db.session.commit()
            except IntegrityError as exception:
                db.session.rollback()
                # TODO: testing [Arlena]
                flash('Failed to edit the translation of episode {0}. Tech data: {0!r}'.format(
                    episode_no, exception
                ), 'error')
                return render_template('admin_pages/edit_episode_translation.html', form=form, episode_no=episode_no,
                                       language_id=language_id)
            else:
                flash('Successfully edited the {0} translation of episode {1}'.format(
                    details.language.name, episode_no
                ), 'info')
                return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))


class EpisodeViewDetails(View):
    """View that shows the details of an episode, giving more info than the episode index"""
    endpoint = 'episode_details'
    decorators = [login_required, role_access]

    def dispatch_request(self, episode_no):
        episode = Episode.query.filter(Episode.episode_no == episode_no).first()
        if not episode:
            flash('Episode not found', 'error')
            return redirect(url_for('.{0}'.format(EpisodeIndex.endpoint)))

        # TODO: complete template in the morning
        return render_template('admin_pages/episode_details.html', episode=episode)


class EpisodeEditSection(MethodView):
    """View that shows the form to edit a section of an episode"""
    endpoint = 'edit_episode_section'
    decorators = [login_required, role_access]

    def get(self, episode_no, language_id, section_no):
        if section_no == -1:
            # New section
            form = EpisodeSectionForm()
            return render_template('admin_pages/edit_episode_section.html', episode_no=episode_no,
                                   language_id=language_id, current_section_no=section_no, form=form)
        else:
            # Get info about section from database
            section = EpisodeSection.query.filter(and_(
                EpisodeSection.episode_no == episode_no,
                EpisodeSection.section_no == section_no,
                EpisodeSection.language_id == language_id
            )).first()
            if not section:
                flash('Section not found', 'error')
                return redirect(url_for('.{0}'.format(EpisodeTranslationDetails.endpoint), episode_no=episode_no,
                                        language_id=language_id))

            try:
                text = section.text
            except RevisionNotFoundException:
                text = ''

            form = EpisodeSectionForm()
            form.section_no.data = section_no
            form.section_text.data = text

            return render_template('admin_pages/edit_episode_section.html', episode_no=episode_no,
                                   language_id=language_id, current_section_no=section_no, form=form)

    def post(self, episode_no, language_id, section_no):
        form = EpisodeSectionForm()

        if not form.validate_on_submit():
            return render_template('admin_pages/edit_episode_section.html', episode_no=episode_no,
                                   language_id=language_id, current_section_no=section_no, form=form)

        if section_no == -1:
            # TODO: Check if the combination of episode and language exists

            # New section, let the fun start...
            # TODO: Do not trust client side validation and check `form.selection_text.data` before inserting
            section = EpisodeSection(episode_no, form.section_no.data, language_id)
            text = EpisodeText(form.section_text.data)

            db.session.add_all([section, text])
            db.session.commit()

            # Push together the first revision of this section
            revision = EpisodeRevision(section.id, text.id, current_user.id, datetime.datetime.utcnow())
            db.session.add(revision)
            db.session.commit()

            # Finalise the section by adding the revision id
            section.current_revision_id = revision.id
            db.session.commit()

            flash('Successfully created section {0} for language {1} in episode {2}'.format(
                section.section_no, section.language.name, episode_no
            ), 'info')
            return redirect(url_for('.{0}'.format(EpisodeTranslationDetails.endpoint), episode_no=episode_no,
                                    language_id=language_id))
        else:
            # Get info about section from database
            section = EpisodeSection.query.filter(and_(
                EpisodeSection.episode_no == episode_no,
                EpisodeSection.section_no == section_no,
                EpisodeSection.language_id == language_id
            )).first()
            if not section:
                flash('Section not found', 'error')
                return redirect(url_for('.{0}'.format(EpisodeTranslationDetails.endpoint), episode_no=episode_no,
                                        language_id=language_id))

            current_revision_id = section.current_revision_id

            try:
                current_text = section.text
            except RevisionNotFoundException:
                # No revision present, should not be possible. Raise exception to stop processing
                # TODO: Implement handling of this exception
                raise IncompleteEpisodeSectionException

            if current_text != form.section_text.data:
                # Text was edited, make a new revision
                text = EpisodeText(form.section_text.data)
                db.session.add(text)
                db.session.commit()

                revision = EpisodeRevision(section.id, text.id, current_user.id, datetime.datetime.utcnow(),
                                           current_revision_id)
                db.session.add(revision)
                db.session.commit()

                section.current_revision_id = revision.id
                db.session.commit()

            section.section_no = form.section_no.data

            try:
                db.session.commit()  # Might trigger an integrity error
            except IntegrityError:
                db.session.rollback()
                # TODO: Test, test, test!!!
                flash('This combination of section number, episode number and language does already exist. '
                      'Please check if you are editing the correct section.')
                form.section_no.errors.append(
                    'This section number is already in use in combination with episode number {0} and language {1}.'
                    .format(episode_no, section.language.name)
                )
                return render_template('admin_pages/edit_episode_section.html', episode_no=episode_no,
                                       language_id=language_id, current_section_no=section_no, form=form)
            else:
                flash('Updated episode {0}, section {1} in {2}'.format(episode_no, section.section_no,
                                                                       section.language.name),
                      'info')
                return redirect(url_for('.{0}'.format(EpisodeTranslationDetails.endpoint), episode_no=episode_no,
                                        language_id=language_id))

