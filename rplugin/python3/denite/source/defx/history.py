# ============================================================================
# FILE: defx/history.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from neovim import Nvim
from ..base import Base


class Source(Base):

    def __init__(self, vim: Nvim):
        super().__init__(vim)

        self.name = 'defx/history'
        self.kind = 'command'
        self._histories = []

    def on_init(self, context: dict):
        if self.vim.current.buffer.options.get('filetype', '') != 'defx':
            return

        self._histories = reversed(self.vim.vars['defx#_histories'])

    def gather_candidates(self, context: dict):
        return [{
            'word': x,
            'abbr': x + '/',
            'action__command': f"call defx#_do_action('cd', ['{x}'])"
        } for x in self._histories]
