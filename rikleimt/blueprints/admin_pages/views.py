# encoding=utf-8
from flask import render_template, url_for, flash, request, redirect
from flask.views import View, MethodView
from flask_login import login_required, login_user, logout_user

from sqlalchemy.exc import IntegrityError

from rikleimt.blueprints.admin_pages.forms import (
    LoginForm, KepaWochaUserFormCreate, KepaWochaUserFormEdit, RoleForm, PageAccessForm, RoleHelperForm, LanguageForm
)
from rikleimt.decorators import role_access
from rikleimt.models import db, User, Role, PageAccess, Language


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
                login_user(user, form.remember.data)

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


class KepaWochaUsers(View):
    endpoint = 'kepa_wocha_users'
    decorators = [login_required, role_access]

    def dispatch_request(self):
        users = User.query.all()

        return render_template('admin_pages/kepa_wocha_users.html', users=users)


class KepaWochaEditUser(MethodView):
    # TODO: Optimise (DRY) [Arlena]
    endpoint = 'kepa_wocha_edit_user'
    decorators = [login_required, role_access]

    @staticmethod
    def _prepare_form(form):
        form.role.choices = [(r.id, r.name) for r in Role.query.all()]
        return form

    def get(self, user_id):
        if user_id == -1:
            # New user
            form = self._prepare_form(KepaWochaUserFormCreate())
        else:
            user = User.query.filter(User.id == user_id).first()
            if not user:
                flash('The user that was selected to edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(KepaWochaUsers.endpoint)))

            form = self._prepare_form(KepaWochaUserFormEdit())

            form.email.data = user.email
            form.role.data = user.role_id
            form.activated.data = user.activated

        return render_template('admin_pages/kepa_wocha_user_edit.html', form=form, user_id=user_id)

    def post(self, user_id):
        if user_id == -1:
            # New user
            form = self._prepare_form(KepaWochaUserFormCreate())
        else:
            user = User.query.filter(User.id == user_id).first()
            if not user:
                flash('The user that was selected to edit does not exist.', 'error')
                return redirect(url_for('.{0}'.format(KepaWochaUsers.endpoint)))

            form = self._prepare_form(KepaWochaUserFormEdit())

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
                    return render_template('admin_pages/kepa_wocha_user_edit.html', form=form, user_id=user_id)
                else:
                    flash('Successfully created the new user.')
                    return redirect(url_for('.{0}'.format(KepaWochaUsers.endpoint)))
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
                    return render_template('admin_pages/kepa_wocha_user_edit.html', form=form, user_id=user_id)
                else:
                    flash('Successfully edited the user.', 'info')
                    return redirect(url_for('.{0}'.format(KepaWochaUsers.endpoint)))

        return render_template('admin_pages/kepa_wocha_user_edit.html', form=form, user_id=user_id)


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
            form.in_menu = form.in_menu.data
            form.is_administrative = form.is_administrative.data

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
