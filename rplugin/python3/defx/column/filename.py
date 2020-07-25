# ============================================================================
# FILE: filename.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base, Highlights
from defx.context import Context
from defx.util import Nvim, Candidate, len_bytes, strwidth
from defx.view import View

import typing


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'filename'
        self.vars = {
            'min_width': 40,
            'max_width': 100,
            'root_marker_highlight': 'Constant',
        }
        self.is_stop_variable = True
        self.has_get_with_highlights = True

        self._current_length = 0
        self._syntaxes = [
            'directory',
            'directory_marker',
            'root',
            'root_marker',
        ]
        self._context: Context = Context()
        self._directory_marker = '**'
        self._file_marker = '||'

    def on_init(self, view: View, context: Context) -> None:
        self._context = context

    def get_with_variable_text(
            self, context: Context, variable_text: str, candidate: Candidate
    ) -> typing.Tuple[str, Highlights]:
        text = variable_text
        highlights = []

        if not context.with_highlights:
            text += (self._directory_marker
                     if candidate['is_directory'] and not candidate['is_root']
                     else self._file_marker)

        if context.with_highlights and candidate['is_directory']:
            if candidate['is_root']:
                root_len = len_bytes(candidate['root_marker'])
                highlights = [
                    (f'{self.highlight_name}_root_marker',
                     self.start, root_len),
                    (f'{self.highlight_name}_root',
                     self.start + root_len,
                     len_bytes(candidate['word']) - root_len),
                ]
            else:
                highlights = [(f'{self.highlight_name}_directory',
                               self.start, len_bytes(candidate['word']))]

        text += candidate['word']
        return (self._truncate(text), highlights)

    def length(self, context: Context) -> int:
        max_fnamewidth = max([strwidth(self.vim, x['word'])
                              for x in context.targets])
        max_fnamewidth += context.variable_length
        max_fnamewidth += len(self._file_marker)
        max_width = int(self.vars['max_width'])
        if max_width < 0:
            max_width = int(-max_width * context.winwidth / 100)
        self._current_length = max(
            min(max_fnamewidth, max_width),
            int(self.vars['min_width']))
        return self._current_length

    def syntaxes(self) -> typing.List[str]:
        return [self.syntax_name + '_' + x for x in self._syntaxes]

    def highlight_commands(self) -> typing.List[str]:
        commands: typing.List[str] = []

        directory_marker = self.vim.call(
            'escape', self._directory_marker, r'~/\.^$[]*')
        commands.append(
            r'syntax match {0}_{1} /{2}/ conceal contained '
            'containedin={0}_directory'.format(
                self.syntax_name, 'directory_marker', directory_marker))
        commands.append(
            r'syntax match {0}_{1} /{2}\%(.{3}[{4}/]\)\+/ '
            'contained containedin={0}'.format(
                self.syntax_name, 'directory', directory_marker, r'\{-}',
                '\\' if self.vim.call('defx#util#is_windows') else ''))

        file_marker = self.vim.call(
            'escape', self._file_marker, r'~/\.^$[]*')
        commands.append(
            r'syntax match {0}_{1} /{2}/ conceal contained '
            'containedin={0}_file'.format(
                self.syntax_name, 'file_marker', file_marker))
        commands.append(
            r'syntax match {0}_{1} /{2}.{3}/ '
            'contained containedin={0}'.format(
                self.syntax_name, 'file', file_marker, r'\{-}'))

        root_marker = self.vim.call(
            'escape', self._context.root_marker, r'~/\.^$[]*')
        commands.append(
            r'syntax match {0}_{1} /{2}/ contained '
            'containedin={0}_root'.format(
                self.syntax_name, 'root_marker', root_marker))
        commands.append(
            r'syntax match {0}_{1} /{2}.*/ contained '
            'containedin={0}'.format(
                self.syntax_name, 'root', root_marker))

        commands.append(
            'highlight default link {}_{} {}'.format(
                self.highlight_name, 'directory', 'PreProc'))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.highlight_name, 'root_marker',
                self.vars['root_marker_highlight']))
        commands.append(
            'highlight default link {}_{} {}'.format(
                self.highlight_name, 'root', 'Identifier'))

        return commands

    def _truncate(self, word: str) -> str:
        width = strwidth(self.vim, word)
        max_length = self._current_length
        if (width > max_length or
                len(word) != len(bytes(word, 'utf-8', 'surrogatepass'))):
            return str(self.vim.call(
                'defx#util#truncate_skipping',
                word, max_length, int(max_length / 3), '...'))

        return word + ' ' * (max_length - width)
