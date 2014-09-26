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

from mentoring.light_children import LightChild, Scope, String
from mentoring import MCQBlock

from ooyala_player import OoyalaPlayerLightChildBlock

from .utils import render_template

# Globals ###########################################################

log = logging.getLogger(__name__)

# Classes ###########################################################

class StepBlock(LightChild):
    """
    A representation of an adventure step.
    """
    content = String(help="Text of the info to provide if needed", scope=Scope.content, default="")
    name = String(help="Name of the step", scope=Scope.content, default=None)
    back = String(help="Name of the back step", scope=Scope.content, default=None)
    next = String(help="Name of the next step", scope=Scope.content, default=None)
    has_children = True

    def render(self, context=None):
        """
        Returns a fragment containing the formatted step
        """
        context = context or {}
        context['as_template'] = False

        fragment, named_children = self.get_children_fragment(
            context, view_name='mentoring_view',
            not_instance_of=(OoyalaPlayerLightChildBlock,)
        )
        fragment.add_content(render_template('templates/html/step.html', {
            'self': self,
            'named_children': named_children,
            'ooyala_players': self.ooyala_players
        }))
        return self.xblock_container.fragment_text_rewriting(fragment)

    @property
    def has_choices(self):
        """
        Returns True if the current_step has choices.
        """

        choices = [child for child in self.get_children_objects() if isinstance(child, MCQBlock)]

        return True if choices else False

    @property
    def ooyala_players(self):
        """
        Returns the ooyala player children.

        TODO: This could be refactored:
              See https://github.com/edx-solutions/xblock-adventure/pull/1/files#r17821141
        """

        players = ([(child.name, child) for child in self.get_children_objects()
                    if isinstance(child, OoyalaPlayerLightChildBlock)])

        return players
