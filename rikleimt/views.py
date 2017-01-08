# encoding=utf-8
from flask import render_template
from flask.views import View


class Login(View):
    # TODO: Move this to the administrative pages blueprint, then add the correct endpoint to the LoginManager
    endpoint = 'login_administrative_pages'

    def dispatch_request(self):
        return 'TODO: Add login system here'


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
