# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.context import Context
from defx.defx import Defx
from neovim import Nvim

import defx.action


class View(object):

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._defx = Defx(self._vim)

        self._vim.command('enew')

        # Define mappings
        self._vim.command('nnoremap <silent><buffer><expr><CR>' +
                          '  defx#do_action("open")')

    def redraw(self) -> None:
        """
        Redraw defx buffer.
        """
        self._candidates = self._defx.gather_candidates()
        options = self._vim.current.buffer.options
        options['modifiable'] = True
        self._vim.current.buffer[:] = [x['word'] for x in self._candidates]
        options['modifiable'] = False
        options['modified'] = False

    def do_action(self, action: str) -> None:
        """
        Do "action" action.
        """
        cursor = self._vim.current.window.cursor

        context = Context(targets=[self._candidates[cursor[0]-1]])

        defx.action.do_action(self._vim, action, context)
