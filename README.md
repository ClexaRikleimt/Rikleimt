# Rikleimt Backend

## To use this repository
1. Copy rikleimt/config.py.example to rikleimt/config.py and edit the configuration values
2. Install the required packages: `pip install -r requirements.txt`
3. Set up the pre-commit git hook on your local repository: `flake8 --install-hook git` 
4. Configure the git hook to prevent commits that do not comply to PEP8 and/or contain syntax errors: `git config --bool flake8.strict true`. To make sure and track all files, also perform `git config --bool flake8.lazy true`. 
5. Run `python run.py` from the top folder to get a development (debug) version running.

## Preparing translations for Slengswichakru:
Requirements: the babel package installed (see step 2 of the repository usage instructions)
For within the Slengswichakru, the [Poedit](https://poedit.net/) program is an easy to use editor to fill in the translation files.

1. Open the command line on your platform and move to the rikleimt folder inside this repository
2. (Within the python environment that has the babel package) use the following command: 
   `pybabel extract -F babel.cfg  -k lazy_gettext -o translations/messages.pot .`
3. Intialise the translations for each translation required: 
   `pybabel init -i translations/messages.pot -d translations -l <language_id>`, where <language_id> 
   is the 2 character identifier for that language, for example 'de' for German
4. Send the translations/<language_id>/LC_MESSAGES/messages.po file to the Slengswichakru for translation
5. Put the returned message.po files given by Slengswichakru back in the translations/<language_id>/LC_MESSAGES/ 
   folder. Overwrite the empty version
6. To compile the translated message.po files into usable translations, use the following command: 
   `pybabel compile -d translations`
7. If the original text changes after it was translated, or if more text is added that has to be 
   translated as well, use the following command: `pybabel update -i translations/messages.pot -d translations`. 
   The changes will then be merged. Repeat step 4, 5 and 6


# Rikleimt-Frontend
Instructions kept for historical uses. Please refer to the steps above for the backend on how to set up the project.

## Setup instructions
1. Install Flask with pip. For this project we are using Python 3.5, since that's the latest version of python supported by Flask.. If you don't have that, you'll have to setup a virtual environment to install flask and run the server. Instructions on installing a virtual environment and using it can be found [here][1]. If you don't mind sticking to 3.5 though, you can install it with `pip install flask`.
2. Move the wow_book folder from the root of wow_book_plugin to static/plugins. The folder can be found on the team google drive.
3. Install all of the required python packages by navigating to the root directory of the repo, and calling `pip install -r requirements.txt`
..* The packages to be installed are: flask sqlalchemy, flask-assets
4. Install maridaDB from the [site][3]. It's around 400 mb.
5. Run run.py

The maria database username is *root* and the password is *sontaim* (that's cool speak for "story").

[1]: http://flask.pocoo.org/docs/0.12/installation/
[2]: http://flask-assets.readthedocs.io/en/latest/
[3]: https://mariadb.com/kb/en/mariadb/getting-installing-and-upgrading-mariadb/

# Development instructions
In order to modify the SCSS, JS, or even add images or fonts, we need to install a few more things.
Gulp is used to compile files and minify them. It takes everything from the /assets/ folder, does some magic and saves the compiled files to /rikleimt/static/.

### Installation:
1. [Install node.js](https://nodejs.org/en/)
2. In the Node.js command prompt, go to the same folder the git is in (also contains a npm-shrinkwrap.json file), and type `npm install`
(can take up to 10 minutes on a Windows system)

### Development:
1. `cd node_modules\.bin\`
2. Gulp commands:
  * To "watch" for everything: `gulp watch`
  * To "watch" for SCSS only: `gulp watchcss`
  * To "watch" for JavaScript only: `gulp watchjs`
  * To compile SCSS once: `gulp buildcss`
  * To compile JavaScript once: `gulp buildjs`
  * To simply build everything: `gulp`

### Important when committing changes:
When committing changes, make sure to commit the generated /static/ files **separately** from your other files. Otherwise it wouldn't be possible to revert files later on, if we needed to.
Eg.:
  * One commit with .scss files with the comment you want.
  * One commit with the .css files and a comment like "Commit generated files".
Then if we want to revert this, we can just revert the .scss commit, call the `gulp` command and we're good to go.

### To add a JavaScript plugin, ideally use Bower:
1. To install Bower: `npm install -g bower`
2. To install a plugin with it, you need to find its Bower name. Usually, you can just google the plugin name and "bower" and it's going to give you something. As long as it's on GitHub, it usually works.
3. If it's not on Bower, you can install it by hand by putting the files inside /static/plugins/ and then including it in the HTML. The /plugins/ folder is the only one from the /static/ folder that is not affected by `gulp` commands.
