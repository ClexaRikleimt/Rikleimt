# encoding=utf-8
from flask import Blueprint

from rikleimt.application import login_manager
from rikleimt.blueprints.admin_pages.views import (
    Login, Logout, Index, KepaWochaUsers, KepaWochaEditUser, Roles, EditRole, AdminPages, EditAdminPage,
    LanguagesIndex, EditLanguage, EpisodeIndex, EditEpisode, EpisodeTranslationDetails, EpisodeEditTranslation,
    EpisodeViewDetails, EpisodeEditSection
)

admin_pages_bp = Blueprint('admin_pages', __name__, static_folder='static', template_folder='templates')

# ======= URL Rules =======================================

admin_pages_bp.add_url_rule('/login', Login.endpoint, view_func=Login.as_view(Login.endpoint), methods=['GET', 'POST'])
admin_pages_bp.add_url_rule('/logout', Logout.endpoint, view_func=Logout.as_view(Logout.endpoint), methods=['GET'])
admin_pages_bp.add_url_rule('/', Index.endpoint, view_func=Index.as_view(Index.endpoint), methods=['GET'])

admin_pages_bp.add_url_rule('/users', KepaWochaUsers.endpoint, methods=['GET'],
                            view_func=KepaWochaUsers.as_view(KepaWochaUsers.endpoint))

kw_edit_user_view = KepaWochaEditUser.as_view(KepaWochaEditUser.endpoint)
admin_pages_bp.add_url_rule('/users/edit', defaults={'user_id': -1}, view_func=kw_edit_user_view,
                            methods=['GET', 'POST'])
admin_pages_bp.add_url_rule('/users/edit/<int:user_id>', view_func=kw_edit_user_view, methods=['GET', 'POST'])

admin_pages_bp.add_url_rule('/roles', Roles.endpoint, methods=['GET'], view_func=Roles.as_view(Roles.endpoint))

edit_role_view = EditRole.as_view(EditRole.endpoint)
admin_pages_bp.add_url_rule('/roles/edit', EditRole.endpoint, defaults={'role_id': -1}, view_func=edit_role_view,
                            methods=['GET', 'POST'])
admin_pages_bp.add_url_rule('/roles/edit/<int:role_id>', EditRole.endpoint, view_func=edit_role_view,
                            methods=['GET', 'POST'])

admin_pages_bp.add_url_rule('/admin_pages', AdminPages.endpoint, methods=['GET'],
                            view_func=AdminPages.as_view(AdminPages.endpoint))

edit_admin_page_view = EditAdminPage.as_view(EditAdminPage.endpoint)
admin_pages_bp.add_url_rule('/admin_pages/edit', EditAdminPage.endpoint, defaults={'page_id': -1},
                            methods=['GET', 'POST'], view_func=edit_admin_page_view)
admin_pages_bp.add_url_rule('/admin_pages/edit/<int:page_id>', EditAdminPage.endpoint, view_func=edit_admin_page_view,
                            methods=['GET', 'POST'])

admin_pages_bp.add_url_rule('/languages', LanguagesIndex.endpoint, methods=['GET', 'POST'],
                            view_func=LanguagesIndex.as_view(LanguagesIndex.endpoint))

edit_language_view = EditLanguage.as_view(EditLanguage.endpoint)
admin_pages_bp.add_url_rule('/languages/edit', EditLanguage.endpoint, defaults={'language_id': -1},
                            methods=['GET', 'POST'], view_func=edit_language_view)
admin_pages_bp.add_url_rule('/languages/edit/<int:language_id>', EditLanguage.endpoint, methods=['GET', 'POST'],
                            view_func=edit_language_view)

# Are you ready for the episodes? Even if you're not, here it is
edit_episode_view = EditEpisode.as_view(EditEpisode.endpoint)
episode_edit_translation_view = EpisodeEditTranslation.as_view(EpisodeEditTranslation.endpoint)
episode_edit_section_view = EpisodeEditSection.as_view(EpisodeEditSection.endpoint)

admin_pages_bp.add_url_rule('/episodes', EpisodeIndex.endpoint, view_func=EpisodeIndex.as_view(EpisodeIndex.endpoint),
                            methods=['GET'])
admin_pages_bp.add_url_rule('/episodes/edit', EditEpisode.endpoint, defaults={'episode_no': -1},
                            methods=['GET', 'POST'], view_func=edit_episode_view)
admin_pages_bp.add_url_rule('/episodes/edit/<int:episode_no>', EditEpisode.endpoint, view_func=edit_episode_view,
                            methods=['GET', 'POST'])
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>', EpisodeViewDetails.endpoint, methods=['GET'],
                            view_func=EpisodeViewDetails.as_view(EpisodeViewDetails.endpoint))
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>/language/<int:language_id>', EpisodeTranslationDetails.endpoint,
                            methods=['GET'],
                            view_func=EpisodeTranslationDetails.as_view(EpisodeEditTranslation.endpoint))
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>/edit', EpisodeEditTranslation.endpoint, methods=['GET', 'POST'],
                            defaults={'language_id': -1}, view_func=episode_edit_translation_view)
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>/edit/language/<int:language_id>',
                            EpisodeEditTranslation.endpoint, methods=['GET', 'POST'],
                            view_func=episode_edit_translation_view)
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>/language/<int:language_id>/section/edit',
                            EpisodeEditSection.endpoint, defaults={'section_no': -1}, methods=['GET', 'POST'],
                            view_func=episode_edit_section_view)
admin_pages_bp.add_url_rule('/episodes/<int:episode_no>/language/<int:language_id>/section/<int:section_no>/edit',
                            EpisodeEditSection.endpoint, methods=['GET', 'POST'], view_func=episode_edit_section_view)

# =========================================================

login_manager.login_view = '{0}.{1}'.format(admin_pages_bp.name, Login.endpoint)

# In case we'd like to translate the backend as well, put a gettext call around the following message
login_manager.login_message = 'Please login before viewing this page'
login_manager.login_message_category = 'error'
