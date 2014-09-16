# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 OpenCraft
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
from uuid import uuid4

from lxml import etree
from StringIO import StringIO

from mentoring.light_children import XBlockWithLightChildren
from mentoring import TitleBlock

from xblock.core import XBlock
from xblock.fields import Scope, String, Integer, List
from xblock.fragment import Fragment

from lazy import lazy

from .info import InfoBlock
from .step import StepBlock
from .utils import load_resource, render_template, render_js_template


# Globals ###########################################################

log = logging.getLogger(__name__)


# Classes ###########################################################

class AdventureBlock(XBlockWithLightChildren):
    """
    An XBlock providing adventure capabilities

    Composed of text, video, questions and steps, this xblock acts like a 'Choose your own
    adventure'.
    """
    adventure_id = String(scope=Scope.settings, default=lambda: uuid4().hex)

    xml_content = String(help="XML content", default='', scope=Scope.content)
    current_step_name = String(help="Keep track of the student assessment progress.",
                               default='', scope=Scope.user_state)

    display_name = String(help="Display name of the component", default="Adventure",
                          scope=Scope.settings)

    JS_TEMPLATES = [
        ('adventure-step-view', 'templates/html/adventure_step_view.html'),
        ('adventure-navigation-view', 'templates/html/adventure_navigation_view.html'),
    ]

    def _get_current_step(self):
        """
        Find the current step in the list with *current_step*. Return a StepBlock object.
        """
        for step in self.steps:
            if step.name == self.current_step_name:
                return step
        return None

    def _get_next_step(self):
        """
        Find the next step. Returns a StepBlock object.
        """
        current_step_found = False
        for step in self.steps:
            if not current_step_found and step.name == self.current_step_name:
                current_step_found = True
            elif current_step_found:
                return step

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

    def _validate_steps(self, steps):
        """
        Validate steps from the studio submission.

        * All steps must have a "name" attribute.
        * All step names must be unique.
        * The first step name must be "first"
        * All back attribute must be a valid step name.

        Raises a ValueError exception on error.
        """

        step_names = []
        for step in steps:
            name = step.attrib.get('name', '')
            if not name or name in step_names:
                raise ValueError('All steps must be a unique.')
            step_names.append(name)

        if step_names and step_names[0] != "first":
            raise ValueError('The first step name must be "first"')

        for step in steps:
            back = step.attrib.get('back', None)
            if back is not None and back not in step_names:
                raise ValueError('All step "back" attributes must be a valid step name.')

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
            response = {
                'result': 'success',
                'step': {
                    'name': current_step.name,
                    'can_go_back': current_step.back if current_step.back else False,
                    'html': step_fragment.content,
                    'is_last_step': self.current_step_name == self.steps[-1].name # TODO, remove
                }
            }

        return response

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
        Check if thr adventure has steps configured.
        """
        return len(self.steps) > 0

    def student_view(self, context):
        fragment = Fragment()
        fragment, named_children = self.get_children_fragment(
            context, view_name='adventure_view',
            not_instance_of=(TitleBlock, InfoBlock, StepBlock)
        )

        # First access, set the current_step to the beginning of the adventure
        if not self.current_step_name and self.has_steps:
            self.current_step_name = self.steps[0].name

        info_fragment = None
        if self.info:
            info_fragment = self.info.render(context={'as_template': False})
        fragment.add_content(render_template(
            'templates/html/adventure.html', {
                'self': self,
                'info_fragment': info_fragment,
            }))
        fragment.add_css_url(self.runtime.local_resource_url(self, 'public/css/adventure.css'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/vendor/underscore-min.js'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/vendor/backbone-min.js'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/vendor/backbone.marionette.min.js'))

        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/adventure.js'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/adventure_controller.js'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/adventure_step_view.js'))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/adventure_navigation_view.js'))

        fragment.add_javascript_url(
            self.runtime.local_resource_url(self,'public/js/adventure_models.js'))

        context={}
        for template in self.JS_TEMPLATES:
            fragment.add_resource(
                render_js_template(template[1], context=context, id=template[0]),
                "text/html"
            )

        fragment.initialize_js('AdventureBlock')

        return fragment

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):

        try:
            event_type = data.pop('event_type')
        except KeyError as e:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        self.runtime.publish(self, event_type, data)
        return {'result':'success'}

    @XBlock.json_handler
    def submit(self, submissions, suffix=''):
        log.debug(u'Received submissions for {}, step "{}":{}'.format(
            self.adventure_id, self.current_step_name, submissions)
        )

        next_step = self._get_next_step()
        if not next_step:
            return {
                'result': 'error',
                'message': 'No next step. current_step: {}'.format(self.current_step_name)
            }

        self.current_step_name = next_step.name
        self.runtime.publish(self, 'progress', {})

        return self._render_current_step()

    @XBlock.json_handler
    def fetch_current_step(self, submissions, suffix=''):
        log.debug(u'Fetching current student step for {}, step "{}"'.format(
            self.adventure_id, self.current_step_name)
        )

        return self._render_current_step()

    @XBlock.json_handler
    def fetch_previous_step(self, submissions, suffix=''):
        log.debug(u'Fetching previous student step for {}, step "{}"'.format(
            self.adventure_id, self.current_step_name)
        )

        previous_step = self._get_previous_step()
        if previous_step:
            self.current_step_name = previous_step.name

        return self._render_current_step()

    @XBlock.json_handler
    def start_over(self, submissions, suffix=''):
        log.debug(u'Start Over {}'.format(self.adventure_id))

        self.current_step_name = "first"

        return self._render_current_step()

    def studio_view(self, context):
        """
        Editing view in Studio
        """
        fragment = Fragment()
        fragment.add_content(render_template('templates/html/adventure_edit.html', {
            'self': self,
            'xml_content': self.xml_content or self.default_xml_content
        }))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/adventure.js'))
        fragment.add_css_url(
            self.runtime.local_resource_url(self, 'public/css/adventure_edit.css'))

        fragment.initialize_js('AdventureEditBlock')

        return fragment

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        log.debug(u'Received studio submissions: {}'.format(submissions))

        success = True
        xml_content = submissions['xml_content']
        try:
            content = etree.parse(StringIO(xml_content))
        except etree.XMLSyntaxError as e:
            response = {
                'result': 'error',
                'message': e.message
            }
        else:
            root = content.getroot()

            try:
                steps = root.findall('step')
                self._validate_steps(steps)
            except ValueError as e:
                success = False
                response = {
                    'result': 'error',
                    'message': e.message
                }
            else:
                response = {
                    'result': 'success'
                }

                # Fix to get the xblock initialzed in edx/XBlock
                adventure_id = self.adventure_id
                if hasattr(adventure_id, '__call__'):
                    self.adventure_id = adventure_id()

                self.xml_content = etree.tostring(content, pretty_print=True)

        log.debug(u'Response from Studio: {}'.format(response))
        return response

    @property
    def default_xml_content(self):
        return render_template('templates/xml/adventure_default.xml', {
            'self': self
        })
