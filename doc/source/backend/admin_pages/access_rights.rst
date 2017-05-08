Limiting access to content
==========================
In order to edit content on the website, a user needs to log in on the administrative pages. At least 1 account is
pre-made. Each page has a list of user roles that have access to that page. Each account belongs to at least 1 user
role. For example, the page where new accounts are created (for security sake it is not possible to create new accounts
on the outside) is only accessible by the user role `Rikleimt3`. Say that you have an account that is not in that user
role, it won't be able to access that page.

Adding new pages
----------------
To add new pages to the administrative part of the side, a couple steps need to be taken to connect everything. First,
make sure that the file containing the view imports the following parts:

.. code-block:: python

   from flask_login import login_required
   from rikleimt.decorators import role_access

Both `login_required` as well as `role_access` are decorators that need to be added to the view handler. When adding
the decorators to the view, `login_required` should be the most inner decorator, followed by `role_access`. For example,
with a view function it would look like this:

.. code-block:: python

   @role_access
   @login_required
   def page_in_admin_pages():
       return 'This page is protected: a user needs to be both logged in as well as have the right role to access.'

To do the same with a view class, use the `decorators` variable on class level:

.. code-block:: python

   from flask.views import View, MethodView

   class PageInAdminPages(View):
       decorators = [login_required, role_access]

       def dispatch_request(self):
           return 'This page is protected: a user needs to be both logged in as well as have the right role to access.'


   class PageInAdminPages2(MethodView):
       decorators = [login_required, role_access]

       def get(self):
           return 'This page is protected: a user needs to be both logged in as well as have the right role to access.'

The next step is adding the access levels to the page. This is done on the website. Make sure to use an account with a
high enough access level. `Rikleimt3` or `Tekkru` should work for this. Choose from the menu 'Administrative' ->
'Page access'. Press the 'create new page' button and enter the required values. The page name is how it is referred to
on the previous page and in the menu. The endpoint is either the user entered endpoint, or if not manually coded, the
generated endpoint. On a view function, this is the name of the function. In the above example, the endpoint would be
`page_in_admin_pages`. Make sure to add the correct blueprint, following the displayed formatting. Check the box for
'display in menu' if you'd like the page to be visible in the menu. Please note that this is the menu on the
administrative side and is not connected to the menu on the public site. Depending on if you check the box for
administrative pages, it will be placed in one of the dropdowns on the menu bar. Finally, a role is chosen. At least
one role needs to be added to a page. As soon as you press 'save', the page will be accessible.

.. warning::

   If the `role_access` decorator is added to a view handler, but the page has not been configured on the website, it
   won't be accessible for any user.

.. note::

   If only the `login_required` decorator is added to a view handler, it will be visible for any logged in user. This is
   useful for pages like the index page and the logout page.
