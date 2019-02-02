# ============================================================================
# FILE: defx/history.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.source.base import Base

from importlib import find_loader
if find_loader('pynvim'):
    from pynvim import Nvim
else:
    from neovim import Nvim


class Source(Base):

    def __init__(self, vim: Nvim):
        super().__init__(vim)

        self.name = 'defx/history'
        self.kind = 'command'
        self._histories = []

    def on_init(self, context: dict):
        options = self.vim.current.buffer.options
        if 'filetype' not in options or options['filetype'] != 'defx':
            return

        self._histories = reversed(self.vim.vars['defx#_histories'])

    def gather_candidates(self, context: dict):
        return [{
            'word': x,
            'abbr': x + '/',
            'action__command': f"call defx#call_action('cd', ['{x}'])"
        } for x in self._histories]
