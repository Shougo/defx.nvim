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
            'directory_icon': '+',
            'indent': ' ',
            'min_width': 40,
            'max_width': 100,
            'opened_icon': '-',
        }

        self._current_length = 0
        self._syntaxes = [
            'directory',
            'directory_icon',
            'hidden',
            'marker',
            'opened_icon',
            'root',
        ]
        self._context: Context = Context()

    def on_init(self, context: Context) -> None:
        self._context = context

    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        if candidate.get('is_opened_tree', False):
            icon = self.vars['opened_icon']
        elif candidate['is_directory']:
            icon = self.vars['directory_icon']
        else:
            icon = ' '
        return self._truncate(
            self.vars['indent'] * candidate['level'] +
            icon + ' ' + candidate['word'])

    def length(self, context: Context) -> int:
        max_fnamewidth = max([self._strwidth(x['word'])
                              for x in context.targets])
        self._current_length = max(
            min(max_fnamewidth, int(self.vars['max_width'])),
            int(self.vars['min_width']))
        return self._current_length

    def syntaxes(self) -> typing.List[str]:
        return [self.syntax_name + '_' + x for x in self._syntaxes]

    def highlight_commands(self) -> typing.List[str]:
        commands: typing.List[str] = []
        for icon, highlight in {
                'directory': 'Special',
                'opened': 'Special',
        }.items():
            commands.append(
                ('syntax match {0}_{1}_icon /[{2}]/ ' +
                 'contained containedin={0}').format(
                    self.syntax_name, icon, self.vars[icon + '_icon']))
            commands.append(
                'highlight default link {}_{}_icon {}'.format(
                    self.syntax_name, icon, highlight))

        commands.append(
            r'syntax match {0}_{1} /\S*\// contained containedin={0}'.format(
                self.syntax_name, 'directory'))
        commands.append(
            (r'syntax match {0}_{1} /\%{2}c\..*/' +
             ' contained containedin={0}').format(
                 self.syntax_name, 'hidden', self.start))
        root_marker = self.vim.call('escape',
                                    self._context.root_marker, r'~/\.^$[]*')
        commands.append(
            r'syntax match {0}_{1} /{2}/ contained '
            'containedin={0}_root'.format(
                self.syntax_name, 'marker', root_marker))
        commands.append(
            r'syntax match {0}_{1} /{2}.*/ contained '
            'containedin={0}'.format(
                self.syntax_name, 'root', root_marker))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'directory', 'PreProc'))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'hidden', 'Comment'))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'marker', 'Constant'))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'root', 'Identifier'))
        return commands

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
