Translations on the website
===========================

The outside facing side will be translated. This will be done in 2 ways:

* The static texts on the site, such as names of pages on the menu, or an 'about the project' page,
  where the text won't change, will be translated using GNU Gettext. To do so, wrap text in templates in the
  ``{{ _('Translatable text') }}`` syntax.
  Example:

  .. code-block:: jinja

     <p>This is a line of text {{ _('and this part is translatable') }}</p>

  In this example, the text 'and this part is translatable' can be translated to another language.

  .. seealso::

     `Jinja2 <http://jinja.pocoo.org/docs/dev/templates/#i18n>`_
         Jinja2 documentation on translations

     `FlaskBabel <https://pythonhosted.org/Flask-Babel/>`_
         FlaskBabel, the extension that is being used to allow translatable context

* The dynamic text, which is the biggest part of the site, will be stored in the database, pointing to the relevant
  language. All the text of the episodes, including eventual title and trigger warnings, will be stored like this,
  just as the text of the side stories, and all the text on the wiki.


Translating static text
-----------------------

To translate all the static text on the site, you will need to have the FlaskBabel package installed. See the regular
development build instructions for installing this package. For use within Slengswichakru, the `Poedit <https://poedit.net/>`_
program is an easy to use editor to fill in the translations.

1. Open the command line on your platform and move to the rikleimt folder inside this repository
2. (Within the python environment that has the babel package) use the following command: ::

     pybabel extract -F babel.cfg  -k lazy_gettext -o translations/messages.pot .

3. Intialise the translations for each translation required: ::

     pybabel init -i translations/messages.pot -d translations -l <language_id>

   In which <language_id> is the identifier for that language, for example 'de' for German
4. Send the translations/<language_id>/LC_MESSAGES/messages.po file to the Slengswichakru for translation
5. Put the returned message.po files given by Slengswichakru back in the translations/<language_id>/LC_MESSAGES/
   folder. Overwrite the empty version
6. To compile the translated message.po files into usable translations, use the following command: ::

     pybabel compile -d translations

7. If the original text changes after it was translated, or if more text is added that has to be
   translated as well, use the following command: ::

     pybabel update -i translations/messages.pot -d translations

   The changes will then be merged. Repeat step 4, 5 and 6
