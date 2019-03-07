# ============================================================================
# FILE: mark.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from defx.util import Nvim

import os
import typing


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'mark'
        self.vars = {
            'directory_icon': '+',
            'length': 1,
            'opened_icon': '-',
            'readonly_icon': 'X',
            'root_icon': ' ',
            'selected_icon': '*',
        }
        self._syntaxes = [
            'directory',
            'opened',
            'readonly',
            'root',
            'selected',
        ]

    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        icon: str = ' ' * self.vars['length']
        if candidate.get('is_selected', False):
            icon = self.vars['selected_icon']
        elif candidate.get('is_root', False):
            icon = self.vars['root_icon']
        elif not os.access(str(candidate['action__path']), os.W_OK):
            icon = self.vars['readonly_icon']
        elif candidate.get('is_opened_tree', False):
            icon = self.vars['opened_icon']
        elif candidate['is_directory']:
            icon = self.vars['directory_icon']
        return icon

    def length(self, context: Context) -> int:
        return typing.cast(int, self.vars['length'])

    def syntaxes(self) -> typing.List[str]:
        return [self.syntax_name + '_' + x for x in self._syntaxes]

    def highlight_commands(self) -> typing.List[str]:
        commands: typing.List[str] = []
        for icon, highlight in {
                'directory': 'Special',
                'opened': 'Special',
                'readonly': 'Comment',
                'root': 'Identifier',
                'selected': 'Statement',
        }.items():
            commands.append(
                ('syntax match {0}_{1} /[{2}]/ ' +
                 'contained containedin={0}').format(
                    self.syntax_name, icon, self.vars[icon + '_icon']))
            commands.append(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, icon, highlight))
        return commands
