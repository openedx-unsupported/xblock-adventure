# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 edX
#
# Authors:
#          Alan Boudreault <alan@alanb.ca>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# Imports ###########################################################

import logging
import textwrap
from io import StringIO
from uuid import uuid4

from lazy import lazy
from lxml import etree
from web_fragments.fragment import Fragment
from xblock.completable import CompletableXBlockMixin
from xblock.core import XBlock
from xblock.fields import UNIQUE_ID, Integer, List, Scope, String

from mentoring.light_children import XBlockWithLightChildren
from mentoring.title import TitleBlock
from adventure.info import InfoBlock
from adventure.step import StepBlock
from adventure.utils import loader

# Globals ###########################################################

log = logging.getLogger(__name__)


DEFAULT_XML_CONTENT = textwrap.dedent("""\
<adventure display_name="Nav tooltip title">
    <title>Title of Simulation</title>
    <info>Description of overall goal of simulation such as walk Mary through understanding how her actions made a situation really hard on the team and impacted the client relationship:</info>

    <step name="first">
      Mary wants to hear your idea.
      <mcq type="choices">
        <question>What idea will you suggest?</question>
        <choice value="last">Tell Mary about my great idea that matches her perception.</choice>
        <choice value="second">Tell Mary about my other idea that doesn't match her perception.</choice>
      </mcq>
    </step>

    <step name="second">
      <html>
        <strong>FEEDBACK</strong>
        <p>Not quite. That wasn't such a good idea. Mary feels confused because you stated something as a fact that doesn't match her perception...</p>
      </html>
      <ooyala-player/>
      <html>
        <p>You need to see if you can get the conversation back on track.</p>
      </html>
      <mcq type="choices">
        <question>What will you say next?</question>
        <choice value="last">(a) Tell me what you think Bob's perception of the meeting was.</choice>
        <choice value="third">(b) I can understand how you thought that, but let's discuss what really happened.</choice>
      </mcq>
    </step>

    <step name="third" back="second">
      <html>
        <strong>FEEDBACK</strong>
        <p>Not quite. It's OK for Mary to show some emotion. Better to give her the space to do so and keep engaged in a conversation...</p>
      </html>
      <ooyala-player/>
      <html>
        <p>Would be great to have a detailed feedback here following the video above... clarifying what happened and why.
        Things to think about as they are prompted to go back and make a better and correct choice to keep the conversation on track.</p>
        <br/>
        <p>Think about this feedback and let's go back and start the conversation again.</p>
      </html>
    </step>

    <step name="last">
      <html>
        <strong>FEEDBACK</strong>
        <p>Great. Mary agrees with you.</p>
      </html>
      <ooyala-player/>
      <html>
      <p>
        Text to be written by curse creators that says the user has reached a successful outcome and directs them to continue
        on with lesson content.
      </p>
      </html>
    </step>

</adventure>
""")

# Classes ###########################################################

@XBlock.needs('i18n')
@XBlock.wants("settings")
class AdventureBlock(CompletableXBlockMixin, XBlockWithLightChildren):
    """
    An XBlock providing adventure capabilities

    Composed of text, video, questions and steps, this xblock acts like a 'Choose your own
    adventure'.
    """
    adventure_id = String(scope=Scope.settings, default=UNIQUE_ID)

    xml_content = String(help="XML content", scope=Scope.content, default=DEFAULT_XML_CONTENT)
    current_step_name = String(help="Keep track of the student assessment progress.",
                               default='', scope=Scope.user_state)
    student_choices = List(help="Store answers of student choices.", default=[],
                           scope=Scope.user_state)

    display_name = String(help="Display name of the component", default="Adventure",
                          scope=Scope.settings)

    CSS_URLS = [
        'public/css/adventure.css'
    ]

    JS_URLS = [
        'public/js/vendor/underscore-min.js',
        'public/js/vendor/backbone-min.js',
        'public/js/vendor/backbone.marionette.min.js',
        'public/js/vendor/jquery.xblock.js',
        'public/js/adventure.js',
        'public/js/adventure_controller.js',
        'public/js/adventure_logger.js',
        'public/js/adventure_step_view.js',
        'public/js/adventure_navigation_view.js',
        'public/js/adventure_models.js'
    ]

    JS_TEMPLATES = [
        ('adventure-step-view-template', 'templates/html/adventure_step_view.html'),
        ('adventure-navigation-view-template', 'templates/html/adventure_navigation_view.html'),
    ]

    def _get_current_step(self):
        """
        Find the current step in the list with *current_step*.

        Return a StepBlock object.
        """
        for step in self.steps:
            if step.name == self.current_step_name:
                return step
        return None

    def _get_next_step(self, next_step_name=None):
        """
        Find the next step. If step_name is specified, look for that name.

        Returns a StepBlock object.
        """
        if next_step_name:
            return self._get_step_by_name(next_step_name)

        current_step = self._get_current_step()
        if current_step and current_step.next and not current_step.has_choices:
            return self._get_step_by_name(current_step.next)

        return None

    def _get_previous_step(self):
        """
        Find the previous step. Returns a StepBlock object.
        """
        current_step = self._get_current_step()
        if current_step and current_step.back:
            for step in self.steps:
                if step.name == current_step.back:
                    return step

        return None

    def _get_step_by_name(self, name):
        """
        Find a step in the list by its name. Return a StepBlock object.
        """
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def _get_student_choice(self, step):
        """
        Return the student choice for a step.
        """
        for choice in reversed(self.student_choices):
            if choice['step'] == step.name:
                return choice['choice']

        return None

    def _save_student_choice(self, submission):
        """
        Save the choice submitted by the student.
        """
        step = self._get_current_step()
        self.student_choices.append({
            'step': step.name,
            'choice': submission['choice']
        })

    def _validate_steps(self, steps):
        """
        Validate steps from the studio submission.

        * All steps must have a "name" attribute.
        * All step names must be unique.
        * The first step name must be "first"
        * All back attribute must be a valid step name.
        * All next attribute must be a valid step name.
        * All mcq must contain choices.
        * All mcq choice values must be a valid step name.

        Raises a ValueError exception on error.
        """

        step_names = []
        for step in steps:
            name = step.attrib.get('name', '')
            if not name or name in step_names:
                raise ValueError('All steps must be a unique.')
            step_names.append(name)

        # TODO remove this constraint everywhere, use steps[0].name
        if step_names and step_names[0] != "first":
            raise ValueError('The first step name must be "first"')

        for step in steps:
            # Check if the back attribute is valid
            back = step.attrib.get('back', None)
            if back is not None and back not in step_names:
                raise ValueError('All step "back" attributes must be a valid step name.')

            # Check if the next attribute is valid
            next = step.attrib.get('next', None)  # pylint: disable=redefined-builtin
            if next is not None and next not in step_names:
                raise ValueError('All step "next" attributes must be a valid step name.')

            # Check if the mcq choice values are valid
            mcq = step.find('mcq')
            if mcq is not None:
                choices = mcq.findall('choice')
                if not choices:
                    raise ValueError('All mcq must contain choices.')
                for choice in choices:
                    value = choice.attrib.get('value', None)
                    if value is None or value not in step_names:
                        raise ValueError('All mcq choice values must be a valid step name.')

    def _render_current_step(self):
        """
        Render the json response of the current step.
        """
        step_names = [step.name for step in self.steps]

        if not self.has_steps:
            response = {
                'result': 'error',
                'message': 'No step in the adventure'
            }
        else:
            if self.current_step_name not in step_names:
                # something change in studio and the step is no more available.
                self.current_step_name = "first"

            current_step = self._get_current_step()
            step_fragment = current_step.render()
            # TODO move this rendering in the StepBlock itself
            response = {
                'result': 'success',
                'step': {
                    'name': current_step.name,
                    'has_back_step': True if current_step.back else False,
                    'has_next_step': True if current_step.next else False,
                    'can_start_over': False if self.current_step_name == 'first' else True,
                    'html': step_fragment.content,
                    'has_choices': current_step.has_choices,
                    'student_choice': self._get_student_choice(current_step),
                    'xblocks': [],
                    # this should only be once in the app config...
                    'is_studio': getattr(getattr(self, 'xmodule_runtime', None), 'is_author_mode', False)
                }
            }

            ooyala_players = current_step.ooyala_players
            for child in ooyala_players:
                xblock = child.xblock_view()
                xblock['data'] = {
                    'step': current_step.name,
                    'child': child.name
                }
                response['step']['xblocks'].append({
                    'id': child.name,
                    'xblock': xblock
                })

        return response

    @property
    def i18n_service(self):
        """ Obtains translation service """
        return self.runtime.service(self, "i18n")

    @property
    def title(self):
        """
        Returns the title child.
        """
        for child in self.get_children_objects():
            if isinstance(child, TitleBlock):
                return child
        return None

    @property
    def info(self):
        """
        Returns the info child.
        """
        for child in self.get_children_objects():
            if isinstance(child, InfoBlock):
                return child
        return None

    @lazy
    def steps(self):
        """
        Returns the step children.
        """
        return [child for child in self.get_children_objects() if isinstance(child, StepBlock)]

    @lazy
    def has_steps(self):
        """
        Check if the adventure has steps configured.
        """
        return len(self.steps) > 0

    def student_view(self, context):
        fragment = Fragment()

        # Check if the student view of a step child has been requested
        context_step_name = context.get('step', None) if context else None
        context_step_child_name = context.get('child', None) if context else None
        if (context_step_name and
                context_step_name == self.current_step_name and
                context_step_child_name):
            step = self._get_step_by_name(context_step_name)
            for child in step.get_children_objects():
                if child.name == context_step_child_name:
                    return child.student_view(context)

        # First access, set the current_step to the beginning of the adventure
        if not self.current_step_name and self.has_steps:
            self.current_step_name = 'first'

        info_fragment = None
        if self.info:
            info_fragment = self.info.render(context={'as_template': False})

        fragment.add_content(loader.render_django_template(
            'templates/html/adventure.html', {
                'self': self,
                'info_fragment': info_fragment,
            }, i18n_service=self.i18n_service))

        for css_url in self.CSS_URLS:
            fragment.add_css_url(self.runtime.local_resource_url(self, css_url))

        for js_url in self.JS_URLS:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, js_url))

        context = {}
        for template in self.JS_TEMPLATES:
            fragment.add_resource(
                loader.render_js_template(template[1], element_id=template[0], context=context, i18n_service=self.i18n_service),
                "text/html"
            )

        fragment.initialize_js('AdventureBlock')

        return fragment

    @property
    def additional_publish_event_data(self):
        return {
            'user_id': self.scope_ids.user_id,
            'component_id': self.adventure_id,
        }

    @XBlock.json_handler
    def submit(self, submissions, suffix=''):
        log.debug(u'Received submissions for {}, step "{}":{}'.format(
            self.adventure_id, self.current_step_name, submissions))

        current_step = self._get_current_step()
        next_step_name = submissions['choice'] if 'choice' in submissions else None
        next_step = self._get_next_step(next_step_name)

        if not current_step or not next_step:
            return {
                'result': 'error',
                'message': 'Invalid next step. current_step_name: {}'.format(self.current_step_name)
            }

        if not next_step_name and current_step.has_choices:
            return {
                'result': 'error',
                'message': 'Invalid submission. current_step_name: {}'.format(self.current_step_name)
            }

        if 'choice' in submissions:
            self._save_student_choice(submissions)
        self.current_step_name = next_step.name
        self.emit_completion(1.0)

        return self._render_current_step()

    @XBlock.json_handler
    def fetch_current_step(self, submissions, suffix=''):
        log.debug(u'Fetching current student step for {}, step "{}"'.format(
            self.adventure_id, self.current_step_name))

        return self._render_current_step()

    @XBlock.json_handler
    def fetch_previous_step(self, submissions, suffix=''):
        log.debug(u'Fetching previous student step for {}, step "{}"'.format(
            self.adventure_id, self.current_step_name))

        previous_step = self._get_previous_step()
        if previous_step:
            self.current_step_name = previous_step.name

        return self._render_current_step()

    @XBlock.json_handler
    def start_over(self, submissions, suffix=''):
        log.debug(u'Start Over {}'.format(self.adventure_id))

        while self.student_choices:
            self.student_choices.pop()

        self.current_step_name = "first"

        return self._render_current_step()

    def studio_view(self, context):
        """
        Editing view in Studio
        """
        fragment = Fragment()
        fragment.add_content(loader.render_django_template('templates/html/adventure_edit.html', {
            'self': self,
            'xml_content': self.xml_content
        }, i18n_service=self.i18n_service))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/adventure.js'))
        fragment.add_css_url(
            self.runtime.local_resource_url(self, 'public/css/adventure_edit.css'))

        fragment.initialize_js('AdventureEditBlock')

        return fragment

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        log.debug(u'Received studio submissions: {}'.format(submissions))

        xml_content = submissions['xml_content']
        try:
            content = etree.parse(StringIO(xml_content))
        except etree.XMLSyntaxError as e:
            response = {
                'result': 'error',
                'message': str(e)
            }
        else:
            root = content.getroot()

            try:
                steps = root.findall('step')
                self._validate_steps(steps)
            except ValueError as e:
                response = {
                    'result': 'error',
                    'message': str(e)
                }
            else:
                response = {
                    'result': 'success'
                }

                # Fix to get the xblock initialized in edx/XBlock
                adventure_id = self.adventure_id
                if callable(adventure_id):
                    self.adventure_id = adventure_id()

                self.xml_content = etree.tostring(content, encoding='unicode', pretty_print=True)

        log.debug(u'Response from Studio: {}'.format(response))
        return response

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [("Adventure scenario", DEFAULT_XML_CONTENT)]
