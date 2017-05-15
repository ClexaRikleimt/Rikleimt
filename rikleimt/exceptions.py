# encoding=utf-8
from werkzeug.exceptions import BadRequest


class APIBadRequestException(BadRequest):
    pass
