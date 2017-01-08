# encoding=utf-8
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# from sqlalchemy import event, DDL

from rikleimt.config import metadata

db = SQLAlchemy(metadata=metadata)

krus_members = db.Table(
    'krus_members',
    metadata,
    db.Column('kru_id', db.Integer, db.ForeignKey('kru.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('project_member.id'))
)

roles_pages = db.Table(
    'roles_pages',
    metadata,
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('page_id', db.Integer, db.ForeignKey('page_access.id'))
)


class Kru(db.Model):
    __tablename__ = 'kru'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode(50), nullable=False)

    members = db.relationship('ProjectMember', secondary=krus_members, back_populates='krus')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.name)


class ProjectMember(db.Model):
    __tablename__ = 'project_member'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode(50), nullable=False)
    twitter = db.Column('twitter', db.Unicode(45), nullable=True)
    tumblr = db.Column('tumblr', db.Unicode(45), nullable=True)

    krus = db.relationship('Kru', secondary=krus_members, back_populates='members')

    def __init__(self, name, twitter=None, tumblr=None):
        self.name = name
        self.twitter = twitter
        self.tumblr = tumblr

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.name)


class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(60), nullable=False)
    locale_code = db.Column(db.Unicode(70), nullable=False)

    def __init__(self, name, locale_code):
        self.name = name
        self.locale_code = locale_code

    def __repr__(self):
        return '<{0} - {1!r} ({2})>'.format(self.__class__.__name__, self.name, self.locale_code)


class Episode(db.Model):
    __tablename__ = 'episode'
    episode_no = db.Column(db.Integer, primary_key=True)
    sfw = db.Column('sfw', db.Boolean(name='sfw'), nullable=False, default=True)

    details = db.relationship('EpisodeDetails', back_populates='episode')

    sections = db.relationship('EpisodeSection', back_populates='episode', order_by='EpisodeSection.section_no')

    def __init__(self, episode_no, sfw):
        self.episode_no = episode_no
        self.sfw = sfw

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.episode_no)


class EpisodeDetails(db.Model):
    __tablename__ = 'episode_details'
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    episode_no = db.Column(db.Integer, db.ForeignKey('episode.episode_no'))

    episode = db.relationship('Episode', back_populates='details', uselist=False)

    title = db.Column(db.Unicode(120), nullable=True)
    warnings = db.Column('trigger_warnings', db.Unicode(1000), nullable=True)

    __table_args__ = (
        db.PrimaryKeyConstraint('language_id', 'episode_no', name='pk_episode_details'),
    )

    def __init__(self, language_id, episode_no, title=None, warnings=None):
        self.language_id = language_id
        self.episode_no = episode_no
        self.title = title
        self.warnings = warnings

    def __repr__(self):
        return '<{0} - episode {1!r} in language {2!r}>'.format(self.__class__.__name__, self.episode_no,
                                                                self.language_id)


class EpisodeSection(db.Model):
    __tablename__ = 'episode_section'
    id = db.Column(db.Integer, primary_key=True)
    episode_no = db.Column(db.Integer, db.ForeignKey('episode.episode_no'), nullable=False)
    section_no = db.Column(db.Integer, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    episode = db.relationship('Episode', back_populates='sections')

    text = db.relationship('EpisodeText', secondary=lambda: EpisodeRevision.__table__,
                           primaryjoin="EpisodeSection.id == EpisodeRevision.section_id",
                           secondaryjoin="EpisodeRevision.text_id == EpisodeText.id",
                           lazy='dynamic', viewonly=True)

    __table_args__ = (
        db.UniqueConstraint('episode_no', 'section_no', 'language_id', name='uq_episode_section_identifier'),
    )

    def __init__(self, episode_no, section_no, language_id):
        self.episode_no = episode_no
        self.section_no = section_no
        self.language_id = language_id

    def __repr__(self):
        return '<{0} - Episode {1}, Section {2} in language {3}>'.format(self.__class__.__name__, self.episode_no,
                                                                         self.section_no, self.language_id)


class EpisodeRevision(db.Model):
    __tablename__ = 'episode_revision'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('episode_section.id'), nullable=False)
    text_id = db.Column(db.Integer, db.ForeignKey('episode_text.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('episode_revision.id'), nullable=True)

    parent = db.relationship(lambda: EpisodeRevision, remote_side=id, uselist=False)

    def __init__(self, section_id, text_id, user_id, timestamp, parent_id=None):
        self.section_id = section_id
        self.text_id = text_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.parent_id = parent_id

    def __repr__(self):
        return '<{0} - {1!r} (section: {2!r})>'.format(self.__class__.__name__, self.id, self.section_id)


class EpisodeText(db.Model):
    __tablename__ = 'episode_text'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.id)


class SideStory(db.Model):
    __tablename__ = 'side_story'
    id = db.Column(db.Integer, primary_key=True)
    sfw = db.Column('sfw', db.Boolean(name='sfw'), nullable=False, default=True)

    details = db.relationship('SideStoryDetails', back_populates='side_story')

    sections = db.relationship('SideStorySection', back_populates='side_story', order_by='SideStorySection.section_no')

    def __init__(self, sfw):
        self.sfw = sfw

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.id)


class SideStoryDetails(db.Model):
    __tablename__ = 'side_story_details'
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    side_story_id = db.Column(db.Integer, db.ForeignKey('side_story.id'))

    title = db.Column(db.Unicode(120), nullable=True)
    warnings = db.Column('trigger_warnings', db.Unicode(1000), nullable=True)

    side_story = db.relationship('SideStory', back_populates='details', uselist=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('language_id', 'side_story_id', name='pk_side_story_details'),
    )

    def __init__(self, language_id, side_story_id, title=None, warnings=None):
        self.language_id = language_id
        self.side_story_id = side_story_id
        self.title = title
        self.warnings = warnings

    def __repr__(self):
        return '<{0} - story {1!r} in language {2!r}>'.format(self.__class__.__name__, self.side_story_id,
                                                              self.language_id)


class SideStorySection(db.Model):
    __tablename__ = 'side_story_section'
    id = db.Column(db.Integer, primary_key=True)
    side_story_id = db.Column(db.Integer, db.ForeignKey('side_story.id'), nullable=False)
    section_no = db.Column(db.Integer, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    side_story = db.relationship('SideStory', back_populates='sections')

    text = db.relationship('SideStoryText', secondary=lambda: SideStoryRevision.__table__,
                           primaryjoin="SideStorySection.id == SideStoryRevision.section_id",
                           secondaryjoin="SideStoryRevision.text_id == SideStoryText.id", viewonly=True)

    __table_args__ = (
        db.UniqueConstraint('side_story_id', 'section_no', 'language_id', name='uq_side_story_section_identifier'),
    )

    def __init__(self, side_story_id, section_no, language_id):
        self.side_story_id = side_story_id
        self.section_no = section_no
        self.language_id = language_id

    def __repr__(self):
        return '<{0} - Side Story {1}, Section {2} in language {3}>'.format(self.__class__.__name__, self.side_story_id,
                                                                            self.section_no, self.language_id)


class SideStoryRevision(db.Model):
    __tablename__ = 'side_story_revision'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('side_story_section.id'), nullable=False)
    text_id = db.Column(db.Integer, db.ForeignKey('side_story_text.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('side_story_revision.id'), nullable=True)

    parent = db.relationship(lambda: SideStoryRevision, remote_side=id, uselist=False)

    def __init__(self, section_id, text_id, user_id, timestamp, parent_id=None):
        self.section_id = section_id
        self.text_id = text_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.parent_id = parent_id

    def __repr__(self):
        return '<{0} - {1!r} (section: {2!r})>'.format(self.__class__.__name__, self.id, self.section_id)


class SideStoryText(db.Model):
    __tablename__ = 'side_story_text'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.id)


# class WBWiki(db.Model):
#     __tablename__ = 'wb_wiki'
#     id = db.Column(db.Integer, primary_key=True)
#


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.Unicode(60), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    activated = db.Column(db.Boolean(name='activated'), nullable=False, default=False)

    role = db.relationship('Role', back_populates='users')

    def __init__(self, email, password, role_id, activated):
        self.email = email
        self.password = password
        self.role_id = role_id
        self.activated = activated

    @property
    def is_active(self):
        return self.activated

    def validate_password(self, password):
        # TODO: Password logic here
        pass

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.email)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(30), nullable=False)

    users = db.relationship('User', back_populates='role')
    pages = db.relationship('PageAccess', secondary=roles_pages, back_populates='roles')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.name)


class PageAccess(db.Model):
    """
        Table for listing the pages where certain roles can have access for.
        Will also be used for listing the pages in editing
    """
    __tablename__ = 'page_access'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)

    roles = db.relationship('Role', secondary=roles_pages, back_populates='pages')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{0} - {1!r}>'.format(self.__class__.__name__, self.name)
