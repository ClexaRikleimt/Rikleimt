from flask import Blueprint
from .views import FirstChapter, NextSection, APIAdminSwapEpisodeSections

api_bp = Blueprint('api', __name__)

api_bp.add_url_rule(
    '/book/episode/<string:lang>/episode/<int:episode>/section/<int:current_section>',
    NextSection.endpoint,
    view_func=NextSection.as_view(NextSection.endpoint),
    methods=['GET']
)
api_bp.add_url_rule(
    '/book/episode/<string:lang>/episode/<int:episode>', FirstChapter.endpoint,
    view_func=FirstChapter.as_view(FirstChapter.endpoint),
    methods=['GET']
)
api_bp.add_url_rule(
    '/admin/episode/section/swap/<int:section_id>/<int:other_section_id>', APIAdminSwapEpisodeSections.endpoint,
    view_func=APIAdminSwapEpisodeSections.as_view(APIAdminSwapEpisodeSections.endpoint),
    methods=['POST']
)
