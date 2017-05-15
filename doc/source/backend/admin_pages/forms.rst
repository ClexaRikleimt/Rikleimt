Admin pages - Forms
===================
All forms that are shown to the users of these pages are created and managed with WTForms, a Python library for creating
forms. WTForms is enhanced with a second plugin, Flask-wtforms, which is used to enhance the experience in combination
with flask. All forms are stored in the `forms.py` file in the `admin_pages` package.

WTForms
-------
WTForms is build on 4 key concepts:

- `Forms` are the core container of WTForms. Forms represent a collection of fields, which can be accessed on the form
dictionary-style or attribute style.
- `Fields` do most of the heavy lifting. Each field represents a data type and the field handles coercing form input to
that datatype. For example, IntegerField and StringField represent two different data types. Fields contain a number of
useful properties, such as a label, description, and a list of validation errors, in addition to the data the field
contains.
- Every field has a `Widget` instance. The widget’s job is rendering an HTML representation of that field. Widget
instances can be specified for each field but every field has one by default which makes sense. Some fields are simply
conveniences, for example TextAreaField is simply a StringField with the default widget being a TextArea.
- In order to specify validation rules, fields contain a list of `Validators`.

Above this, Flask-wtforms extends the functionality. For example, Flask-wtforms includes an enhanced form, the
`FlaskForm`, which is protected against CSRF attacks out of the box. Furthermore, there are a couple of fields and
widgets that are defined in the `form_utils.py` file, to enhance the possibilities and improve user friendliness. The
most notable are the `CKEditorField`, a field which turns a TextArea in a ready to use editor, and several fields of
which the names start with 'BS3'. These are fields that do the same as their normal counterpart, but are ready for
interactions made possible with Bootstrap 3, hence the prefix. For example, they support the field having a help text,
or rather a description with instruction on how to use the field. Some fields will require instructions based on how
the design is set up and will make sure the users understand how to use the field.

For example, this is how the form looks like in code, in which an existing episode can be edited:

.. code-block:: python

  class EditEpisodeForm(FlaskForm):
      episode_no = BS3IntegerField(label='Episode number', validators=[
          InputRequired()
      ])
      sfw = BS3BooleanField(label='Is the episode safe for work? ')
      n_sections = BS3IntegerField(label='How many sections, or scenes, are there in the episode? ', validators=[
          InputRequired()
      ], help_text="""
  The episodes will be uploaded in the same set of scenes as they were written in. For example, the first episode,
  the prologue including, has 7 scenes: prologue, 1, 2, 3, 3B, 4, 5.
  """)

Displaying forms
----------------
In order to display a form to the user, call it in the view handle and pass it forward to the template. For example,
with the form above:

.. code-block:: python

  def view():
      form = EditEpisodeForm()
      return render_template('template.html', form=form)

Then, in the template file, import the form macros that help creating forms at the top, directly after extending the
template.

.. code-block:: jinja2

  {% extends 'admin_pages/base_cms.html' %}
  {% from 'admin_pages/utils/form_macro.html' import render_field, render_field_horizontal %}

.. note::
  There are 2 functions for rendering a form. These are based on the types of forms in Bootstrap3.
  `Regular forms <http://getbootstrap.com/css/#forms>` are rendered with `render_field`, but in `horizontal forms <http://getbootstrap.com/css/#forms-horizontal>`
  fields are rendered in a horizontal (grid) layout. When using this layout, use the `render_field_horizontal` function.

Next, create a form in the template, and call the relevant rendering function for each field in the form. Please see the
`utils/form_macro.html` file in the templates folder to look up the parameters this macro takes.

.. code-block:: jinja2

  <form method="POST" action="{{ url_for('.edit_episode', episode_no=episode_no) }}">
      {{ form.hidden_tag() }}

      {{ render_field(form.episode_no) }}
      {{ render_field(form.sfw) }}
      {{ render_field(form.n_sections) }}

      <div class="form-group">
          <button type="submit" class="btn btn-default">Save</button>
      </div>
  </form>

.. note::
  Calling the `hidden_tag` function on the form, renders the `<input type="hidden">` fields to the page, that are
  required when using the `FlaskForm`. If you forget to call this function, the field won't validate because the CSRF
  token is missing, thus it can't prove it is not a CSRF attack.

Reading the input of the form
-----------------------------
The last part of using the form is done in the view handler again. If there is data present in the request to the server
that was posted, it will automatically be inserted in the form on its creation. The next step is checking if the form
validates. If it doesn't, send the form to the user again. The errors are stored in the fields and displayed to the user
with the rendering functions without further interactions needed. The actual content of the fields is stored in the
`data` attribute of each field. For example, the following snippets shows the input of the form to the user after posting
the form:

.. code-block:: python

  def view():
      form = EditEpisodeForm()

      if not form.validate_on_submit():
          return render_template('template.html', form=form)

      # Form validates
      return "Episode {0} has {1} scenes and {2} SFW.".format(
          form.episode_no.data,
          form.n_sections.data,
          "is" if form.sfw.data else "isn't"
      )
