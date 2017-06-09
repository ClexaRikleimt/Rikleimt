# encoding=utf-8
from .application import create_app, login_manager
from .views import TemplateHome, TemplateBook
from .models import User


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.filter(User.id == int(user_id)).first()
    except (ValueError, AttributeError):
        return None


# TODO: Add routes to app object
app.add_url_rule('/', TemplateHome.endpoint, methods=['GET'], view_func=TemplateHome.as_view(TemplateHome.endpoint))
app.add_url_rule('/book', TemplateBook.endpoint, view_func=TemplateBook.as_view(TemplateBook.endpoint), methods=['GET'])


#   @app.route('/db/addText/')
#   def add_text():
#      from rikleimt.models import db,Language,Episode,EpisodeDetails,EpisodeSection,EpisodeText
#     from rikleimt.models import EpisodeRevision,User
#
#
# @app.route('/db/add/')
# def add_db():
#
#     from rikleimt.models import db,Language,Episode,EpisodeDetails,EpisodeSection,EpisodeText
#     from rikleimt.models import EpisodeRevision, Role, User
#     #db.drop_all()
#     #sdb.create_all()
#
#
#     english = Language('English','En','American')
#     episode = Episode(1,True)
#
#     db.session.add(english)
#
#     db.session.commit()
#     print("English")
#     db.session.add(episode)
#
#     db.session.commit()
#     print("episode")
#     epi = Episode.query.first()
#     lang = Language.query.first()
#     epideet = EpisodeDetails(lang.id,epi.episode_no,title="The adventure begins!",warnings="Some standard warnings")
#     db.session.add(epideet)
#
#
#     db.session.commit()
#     print("Epideets")
#     episode = Episode.query.first()
#     english = Language.query.filter_by(name='English').first()
#
#     role = Role('Tester')
#     db.session.add(role)
#     db.session.commit()
#     role = Role.query.first()
#     user = User('clexarikleimt@gmail.com','sontaim',role.id,True)
#     db.session.add(user)
#     db.session.commit()
#
#
#     with open('chapter 1.txt', encoding="utf8") as f:
#         from datetime import datetime
#         sections = f.read().split('Section')
#         for index,section in enumerate(sections):
#             if section:
#                 sectionRow = EpisodeSection(episode.episode_no,index,english.id)
#                 sectionText = EpisodeText(section)
#                 db.session.add(sectionRow)
#                 db.session.add(sectionText)
#                 db.session.commit()
#                 currentSection = EpisodeSection.query.filter_by(section_no = index).first()
#                 currentText = EpisodeText.query.filter_by(id=index).all()
#                 user = User.query.first()
#
#                 sectionRevision = EpisodeRevision(currentSection.id,currentText[-1].id, user.id, datetime(2017,1,1) )
#                 db.session.add(sectionRevision)
#                 db.session.commit()
#                 print(index)
#
#     return ("All sections were successfully added!")
# #
# @app.route('/db')
# def create_db():
#     from rikleimt.models import db
#     db.create_all()
#     return "Database created"
# #
# #
# @app.route('/db_drop')
# def drop_db():
#     from rikleimt.models import db
#     db.drop_all()
#     return "Database dropped"

if __name__ == '__main__':
    app.run()
