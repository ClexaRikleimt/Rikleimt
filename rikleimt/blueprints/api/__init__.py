from flask import Blueprint
from rikleimt.blueprints.api.views import FirstChapter, NextSection

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
