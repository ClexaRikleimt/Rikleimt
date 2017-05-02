# encoding=utf-8
from werkzeug.routing import BaseConverter


class WikiArticleConverter(BaseConverter):
    def to_python(self, value):
        return value.replace('_', ' ')

    def to_url(self, value):
        return value.replace(' ', '_')
