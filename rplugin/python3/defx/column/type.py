# ============================================================================
# FILE: type.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from neovim import Nvim

import re


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'mark'
        types = [
            {
                'name': 'text', 'pattern': '\.txt$',
                'icon': '[T]', 'highlight': 'Constant'
            },
            {
                'name': 'image', 'pattern': '\.jpg$',
                'icon': '[I]', 'highlight': 'Type'
            },
            {
                'name': 'archive', 'pattern': '\.zip$',
                'icon': '[A]', 'highlight': 'Special'
            },
            {
                'name': 'executable', 'pattern': '\.exe$',
                'icon': '[X]', 'highlight': 'Statement'
            },
        ]
        self.vars = {
            'types': types,
        }
        self._length: int = 0

    def on_init(self) -> None:
        self._length = max([self.vim.call('strwidth', x['icon'])
                            for x in self.vars['types']]) + 1

    def get(self, context: Context, candidate: dict) -> str:
        for t in self.vars['types']:
            if re.search(t['pattern'], candidate['action__path']):
                return t['icon'] + ' '
        return ' ' * self._length

    def length(self) -> int:
        return self._length

    def highlight(self) -> None:
        for t in self.vars['types']:
            self.vim.command(
                ('syntax match {0}_{1} /{2}/ ' +
                 'contained containedin={0}').format(
                    self.syntax_name, t['name'], re.escape(t['icon'])))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, t['name'], t['highlight']))
