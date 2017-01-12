# encoding=utf-8
from wtforms import TextAreaField, BooleanField, StringField, PasswordField, SelectField, IntegerField
from wtforms.widgets import TextArea

# Helpers
BS3_ATTRIBUTES = ['help_text']


class BS3Helper(object):
    def __init__(self, help_text=None):
        self.help_text = help_text


# Fields
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(CKTextAreaField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)


class BS3StringField(StringField):
    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(BS3StringField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)


class BS3SelectField(SelectField):
    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(BS3SelectField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)


class BS3PasswordField(PasswordField):
    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(BS3PasswordField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)


class BS3BooleanField(BooleanField):
    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(BS3BooleanField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)


class BS3IntegerField(IntegerField):
    def __init__(self, **kwargs):
        bs3_kwargs = dict()
        for attr in BS3_ATTRIBUTES:
            if attr in kwargs:
                bs3_kwargs[attr] = kwargs[attr]
                kwargs.pop(attr)

        super(BS3IntegerField, self).__init__(**kwargs)

        self.bs3 = BS3Helper(**bs3_kwargs)
