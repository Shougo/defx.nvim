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
        self._syntaxes = [
            'directory',
            'hidden',
        ]

    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        return self._truncate(candidate['word'])

    def length(self, context: Context) -> int:
        max_fnamewidth = max([self._strwidth(x['word'])
                              for x in context.targets])
        self._current_length = max(
            min(max_fnamewidth, int(self.vars['max_width'])),
            int(self.vars['min_width']))
        return self._current_length

    def syntaxes(self) -> typing.List[str]:
        return [self.syntax_name + '_' + x for x in self._syntaxes]

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

    def _strwidth(self, word: str) -> int:
        return (int(self.vim.call('strwidth', word))
                if len(word) != len(bytes(word, 'utf-8')) else len(word))

    def _truncate(self, word: str) -> str:
        width = self._strwidth(word)
        if (width > self._current_length or
                len(word) != len(bytes(word, 'utf-8'))):
            return str(self.vim.call(
                'defx#util#truncate_skipping',
                word, self._current_length,
                int(self._current_length / 3), '...'))

        return word + ' ' * (self._current_length - width)
