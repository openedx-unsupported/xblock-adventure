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

from ooyala_player.ooyala_player import OoyalaPlayerLightChildBlock

from mentoring.light_children import LightChild, Scope, String
from mentoring.mcq import MCQBlock
from mentoring.step import StepParentMixin
from adventure.utils import loader

# Globals ###########################################################

log = logging.getLogger(__name__)

# Classes ###########################################################


class StepBlock(LightChild, StepParentMixin):
    """
    A representation of an adventure step.

    Note that it is also a StepParentMixin, as MCQs are of StepMixin,
    requiring there parents to be so.
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

        fragment, children = self.get_step_fragment_children(context)
        fragment.add_content(loader.render_template('templates/html/step.html', {
            'self': self,
            'children': children
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
        Returns the ooyala players child.
        """

        ooyala_players = [child for child in self.get_children_objects()
                          if isinstance(child, OoyalaPlayerLightChildBlock)]

        return ooyala_players

    def get_step_fragment_children(self, context=None):
        children = []

        ooyala_children = {}
        for child in self.get_children_objects():
            ooyala_children[child.name] = True if isinstance(child, OoyalaPlayerLightChildBlock) else False

        fragment, named_children = self.get_children_fragment(context)
        for name, child in named_children:
            children.append((name, child, ooyala_children[name]))

        return (fragment, children)
