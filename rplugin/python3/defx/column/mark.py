# ============================================================================
# FILE: mark.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from neovim import Nvim


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'mark'
        self.vars = {
            'selected_icon': '*',
            'root_icon': '-',
            'directory_icon': '+',
        }

    def get(self, context: Context, candidate: dict) -> str:
        if candidate.get('is_selected', False):
            icon = self.vars['selected_icon']
        elif candidate.get('is_root', False):
            icon = self.vars['root_icon']
        elif candidate['is_directory']:
            icon = self.vars['directory_icon']
        else:
            icon = ' '
        return icon + ' '

    def length(self) -> int:
        return 2

    def highlight(self) -> None:
        for icon, syntax in {
                'selected': 'Statement',
                'root': 'Identifier',
                'directory': 'Special',
        }.items():
            self.vim.command(
                ('syntax match {0}_{1} /[{2}]/ ' +
                 'contained containedin={0}').format(
                    self.syntax_name, icon, self.vars[icon + '_icon']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, icon, syntax))
