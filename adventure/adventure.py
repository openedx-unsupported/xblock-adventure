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
import uuid

from lxml import etree
from StringIO import StringIO

from xblock.core import XBlock
from xblock.fields import Scope, String, Integer, List
from xblock.fragment import Fragment

from .utils import load_resource, render_template, render_js_template


# Globals ###########################################################

log = logging.getLogger(__name__)


# Classes ###########################################################

class AdventureBlock(XBlock):
    """
    An XBlock providing adventure capabilities

    Composed of text, video, questions and steps, this xblock acts like a 'Choose your own
    adventure'.
    """
    url_name = String(help="Name of the current step, used for URL building",
                      default='adventure-default', scope=Scope.content)
    xml_content = String(help="XML content", default='', scope=Scope.content)
    current_step = Integer(help="Keep track of the student assessment progress.",
                   default=1, scope=Scope.user_state, enforce_type=True)

    previous_steps = List(help="List of the previous step for the go back functionnality.",
                          default=[], scope=Scope.user_state)
    display_name = String(help="Display name of the component", default="Adventure",
                          scope=Scope.settings)

    JST = [
        ('adventure-step-view', 'templates/html/adventure_step_view.html'),
        ('adventure-navigation-view', 'templates/html/adventure_navigation_view.html'),
    ]

    def _find_element(self, name):
        try:
            content = etree.parse(StringIO(self.xml_content))
        except etree.XMLSyntaxError as e:
            return None

        return content.getroot().find(name)

    def _find_elements(self, name):
        try:
            content = etree.parse(StringIO(self.xml_content))
        except etree.XMLSyntaxError as e:
            return None

        return content.getroot().findall(name)

    @property
    def title(self):
        """
        Returns the title child.

        Temporary, will be replaced with light child.
        """
        title = self._find_element('title')
        if title is not None:
            return title.text

        return None

    @property
    def info(self):
        """
        Returns the info child.

        Temporary, will be replaced with light children.
        """
        info = self._find_element('info')
        if info is not None:
            return info.text

        return None

    @property
    def steps(self):
        """
        Returns the info child.

        Temporary, will be replaced with light children.
        """
        steps = self._find_elements('step')

        if steps is None:
            steps = []

        return steps

    def student_view(self, context):
        fragment = Fragment()
        # fragment, named_children = self.get_children_fragment(
        #     context, view_name='adventure_view',
        #     not_instance_of=(MentoringMessageBlock, TitleBlock)
        # )

        fragment.add_content(render_template(
            'templates/html/adventure.html',
            {'self': self}
        ))
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
        for template in self.JST:
            fragment.add_resource(
                render_js_template(template[1], context=context, id=template[0]),
                "text/html"
            )

        fragment.initialize_js('AdventureBlock')

        return fragment

    def _get_current_step(self):
        steps = self.steps
        num_steps = len(steps)
        if num_steps == 0 or self.current_step > num_steps:
            return {
                'result': 'error',
                'message': 'Invalid current step: num_steps: {}, current_step: {}'.format(
                    num_steps, self.current_step
                )
            }

        step = steps[self.current_step-1]
        return {
            'result': 'success',
            'step': {
                'name': step.attrib.get('name', ''),
                'can_go_back': step.attrib.get('back', False),
                'html': '<p>{}</p>'.format(step.text),
                'is_last_step': self.current_step == num_steps #temporary, will me removed
            }
        }

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
        log.info(u'Received submissions: {}'.format(submissions))

        next_step = self.current_step + 1
        steps = self.steps
        if next_step > len(steps):
            return {
                'result': 'error',
                'message': 'No next step. current_step: {}'.format(self.current_step)
            }

        self.previous_steps.append(self.current_step)
        self.current_step = next_step
        self.runtime.publish(self, 'progress', {})

        return self._get_current_step()

    @XBlock.json_handler
    def fetch_current_step(self, submissions, suffix=''):
        log.info(u'Fetching current student step.')

        return self._get_current_step()

    @XBlock.json_handler
    def fetch_previous_step(self, submissions, suffix=''):
        log.info(u'Fetching previous student step.')

        steps = self.steps
        if len(steps) > 0:
            step = self.steps[self.current_step-1]
            can_go_back = step.attrib.get('back', False),
            if can_go_back and self.previous_steps:
                self.current_step = self.previous_steps.pop()

        return self._get_current_step()

    @XBlock.json_handler
    def start_over(self, submissions, suffix=''):
        log.info(u'Start Over the adventure.')

        self.current_step = 1

        return self._get_current_step()

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
        log.info(u'Received studio submissions: {}'.format(submissions))

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

            # validate step name
            names = []
            for step in root.findall('step'):
                name = step.attrib.get('name', '')
                if name and name in names:
                    success = False
                    response = {
                        'result': 'error',
                        'message': 'Step names must be unique'
                    }
                    break
                names.append(name)

            if success:
                response = {
                    'result': 'success'
                }
                url_name = root.attrib.get('url_name', '')
                if url_name:
                    self.url_name = url_name
                self.xml_content = etree.tostring(content, pretty_print=True)

        log.debug(u'Response from Studio: {}'.format(response))
        return response

    @property
    def default_xml_content(self):
        return render_template('templates/xml/adventure_default.xml', {
            'self': self,
            'url_name': self.url_name_with_default,
        })

    @property
    def url_name_with_default(self):
        """
        Ensure the `url_name` is set to a unique, non-empty value.
        This should ideally be handled by Studio, but we need to declare the attribute
        to be able to use it from the workbench, and when this happen Studio doesn't set
        a unique default value - this property gives either the set value, or if none is set
        a randomized default value
        """
        if self.url_name == 'adventure-default':
            return 'adventure-{}'.format(uuid.uuid4())
        else:
            return self.url_name
