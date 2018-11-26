# ============================================================================
# FILE: mark.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from defx.util import Nvim

import os


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'mark'
        self.vars = {
            'selected_icon': '*',
            'root_icon': '-',
            'readonly_icon': 'X',
            'directory_icon': '+',
        }

    def get(self, context: Context, candidate: dict) -> str:
        icon: str = ' '
        if candidate.get('is_selected', False):
            icon = self.vars['selected_icon']
        elif candidate.get('is_root', False):
            icon = self.vars['root_icon']
        elif not os.access(str(candidate['action__path']), os.W_OK):
            icon = self.vars['readonly_icon']
        elif candidate['is_directory']:
            icon = self.vars['directory_icon']
        return icon

    def length(self, context: Context) -> int:
        return 1

    def highlight(self) -> None:
        for icon, highlight in {
                'selected': 'Statement',
                'root': 'Identifier',
                'readonly': 'Comment',
                'directory': 'Special',
        }.items():
            self.vim.command(
                ('syntax match {0}_{1} /[{2}]/ ' +
                 'contained containedin={0}').format(
                    self.syntax_name, icon, self.vars[icon + '_icon']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, icon, highlight))
