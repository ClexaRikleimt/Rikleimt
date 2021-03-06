# encoding=utf-8
import json

from flask import make_response
from flask.views import View, MethodView
from flask_login import login_required

from ...decorators import role_access
from ...exceptions import APIBadRequestException
from ...models import EpisodeSection, EpisodeDetails, db


class FirstChapter(View):
    endpoint = 'first_chapter'

    def dispatch_request(self, lang, episode):
        section = EpisodeSection.query.filter_by(episode_no=1, section_no=1).first()
        if section:
            print("section found!")
        else:
            print("Section doesn't exist")
        return_text = section.text.first().content
        return_json = json.dumps({'text': return_text})
        return return_json, 200, {'ContentType': 'application/json'}


class NextSection(View):
    endpoint = 'next_section'

    def dispatch_request(self, lang, episode, current_section):
        section = EpisodeSection.query.filter_by(episode_no=episode, section_no=current_section + 1).first()
        if section is None:
            #  If there isn't a next section, then check for another chapter
            next_chapter = EpisodeSection.query.filter_by(episode_no=episode + 1, section_no=1).first()
            if next_chapter is None:
                return_text = "Check back later for the next chapter! Alternatively, read the listed wiki sections"
                return_json = json.dumps({'text': return_text, 'end': True})
            else:
                episode1 = episode + 1
                details = (
                    EpisodeDetails.query
                    .join(EpisodeSection, EpisodeSection.episode_no == EpisodeDetails.episode_no)
                    .add_columns(EpisodeDetails.title, EpisodeDetails.warnings)
                    .filter(EpisodeSection.episode_no == episode1 and EpisodeSection.section_no == 1)
                    #  Changed to filter because EpisodeSection.episode_no = episode1
                    #  was being interpreted as an expression
                    .first()
                )
                trigger_string = details.warnings
                title = details.title
                return_text = next_chapter.text.first().content
                return_json = json.dumps({
                    'text': return_text,
                    'triggers': trigger_string,
                    'title': title,
                    'end': False
                })
        else:
            #  if the section is in the database then just send it back
            return_text = section.text.first().content
            return_json = json.dumps({'text': return_text})
        return return_json, 200, {'ContentType': 'application/json'}


class APIAdminSwapEpisodeSections(MethodView):
    endpoint = 'admin_swap_episode_sections'
    decorators = [login_required, role_access]

    def post(self, section_id, other_section_id):
        section = EpisodeSection.query.filter(EpisodeSection.id == section_id).first()
        if not section:
            raise APIBadRequestException()

        other_section = EpisodeSection.query.filter(EpisodeSection.id == other_section_id).first()
        if not other_section:
            raise APIBadRequestException()

        if section.episode_no != other_section.episode_no or section.language_id != other_section.language_id:
            # Not in the same translation of the same episode
            raise APIBadRequestException()

        section.section_no, other_section.section_no = other_section.section_no, section.section_no

        db.session.commit()

        response = make_response(json.dumps({
            'status': 200,
            'message': u'Swapped section_no (position) of sections {0} and {1}'.format(section_id, other_section_id)
        }))
        response.mimetype = 'application/json'

        return response
