# ============================================================================
# FILE: filename.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from defx.util import Nvim

import typing


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'filename'
        self.vars = {
            'min_width': 40,
            'max_width': 100,
        }

        self._current_length = 0

    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        spaces_len = self._current_length - len(candidate['word'])
        return str(candidate['word'] + (' ' * spaces_len))

    def length(self, context: Context) -> int:
        def strwidth(word):
            return (self.vim.call('strwidth', word)
                    if len(word) != len(bytes(word, 'utf-8')) else len(word))
        max_fnamewidth = max([strwidth(x['word']) for x in context.targets])
        self._current_length = max(
            min(max_fnamewidth, int(self.vars['max_width'])),
            int(self.vars['min_width']))
        return self._current_length

    def highlight(self) -> None:
        self.vim.command(
            r'syntax match {0}_{1} /.*\// contained containedin={0}'.format(
                self.syntax_name, 'directory'))
        self.vim.command(
            (r'syntax match {0}_{1} /\%{2}c\..*/' +
             ' contained containedin={0}').format(
                 self.syntax_name, 'hidden', self.start))
        self.vim.command(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'directory', 'PreProc'))
        self.vim.command(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'hidden', 'Comment'))
