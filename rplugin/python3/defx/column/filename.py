# ============================================================================
# FILE: filename.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from neovim import Nvim


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'filename'
        self.vars = {
            'length': 100,
        }

    def get(self, context: Context, candidate: dict) -> str:
        spaces_len = self.vars['length'] - len(candidate['abbr'])
        return candidate['abbr'] + (' ' * spaces_len)  # type: ignore

    def length(self) -> int:
        return self.vars['length']

    def highlight(self) -> None:
        self.vim.command(
            'syntax match {0}_{1} /.*\// contained containedin={0}'.format(
                self.syntax_name, 'directory'))
        self.vim.command(
            ('syntax match {0}_{1} /\%{2}c\..*/' +
             ' contained containedin={0}').format(
                 self.syntax_name, 'hidden', self.start))
        self.vim.command(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'directory', 'PreProc'))
        self.vim.command(
            'highlight default link {}_{} {}'.format(
                self.syntax_name, 'hidden', 'Comment'))
