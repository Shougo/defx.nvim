# ============================================================================
# FILE: icon.py
# AUTHOR: GuoPan Zhao <zgpio@qq.com>
#         Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base, Highlights
from defx.context import Context
from defx.util import Nvim, Candidate, len_bytes

import typing


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'icon'
        self.vars = {
            'length': 1,
            'directory_icon': '+',
            'opened_icon': '-',
            'root_icon': ' ',
        }
        self.has_get_with_highlights = True

        self._syntaxes = [
            'directory_icon',
            'opened_icon',
            'root_icon',
        ]
        self._highlights = {
            'directory': 'Special',
            'opened': 'Special',
            'root': 'Identifier',
        }

    def get_with_highlights(
        self, context: Context, candidate: Candidate
    ) -> typing.Tuple[str, Highlights]:
        if candidate['is_opened_tree']:
            return (self.vars['opened_icon'],
                    [(self._highlights['opened'],
                      self.start, len_bytes(self.vars['opened_icon']))])
        elif candidate['is_root']:
            return (self.vars['root_icon'],
                    [(self._highlights['root'],
                      self.start, len_bytes(self.vars['root_icon']))])
        elif candidate['is_directory']:
            return (self.vars['directory_icon'],
                    [(self._highlights['directory'],
                      self.start, len_bytes(self.vars['directory_icon']))])

        return (' ', [])

    def length(self, context: Context) -> int:
        return typing.cast(int, self.vars['length'])

    def syntaxes(self) -> typing.List[str]:
        return [self.syntax_name + '_' + x for x in self._syntaxes]

    def highlight_commands(self) -> typing.List[str]:
        commands: typing.List[str] = []
        for icon, highlight in self._highlights.items():
            commands.append(
                ('syntax match {0}_{1}_icon /[{2}]{3}/ ' +
                 'contained containedin={0}').format(
                     self.syntax_name, icon, self.vars[icon + '_icon'],
                     ' ' if self.is_within_variable else ''
                 ))
            commands.append(
                'highlight default link {}_{}_icon {}'.format(
                    self.syntax_name, icon, highlight))

        return commands
