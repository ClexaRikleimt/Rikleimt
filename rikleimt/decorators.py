# encoding=utf-8
from functools import wraps

from flask import request
from flask_login import current_user, login_required

from werkzeug.exceptions import Forbidden


def role_access(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            if request.endpoint not in current_user.pages.keys():
                raise Forbidden('You do not have the rights to visit this page.')
            else:
                return func(*args, **kwargs)
        except AttributeError:
            # current_user is None
            return login_required(func)
    return decorated_view
