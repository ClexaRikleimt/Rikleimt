# encoding=utf-8
from flask import render_template
from flask.views import View


class TemplateBook(View):
    endpoint = 'template_book'

    def dispatch_request(self):
        # TODO: handler / decent endpoint name
        return render_template('book.html')


class TemplateHome(View):
    endpoint = 'template_home'

    def dispatch_request(self):
        # TODO: handler / decent endpoint name
        return render_template('index.html')
