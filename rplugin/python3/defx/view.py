# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.defx import Defx
import defx.action


class View(object):

    def __init__(self, vim):
        self._vim = vim
        self._defx = Defx(self._vim)

        self._vim.command('enew')

        # Define mappings
        self._vim.command('nnoremap <silent><buffer><expr><CR>' +
                          '  defx#do_action("open")')

    def redraw(self):
        self._candidates = self._defx.gather_candidates()
        self._vim.current.buffer[:] = [x['word'] for x in self._candidates]

    def do_action(self, action):
        cursor = self._vim.current.window.cursor

        context = {}
        context['targets'] = [self._candidates[cursor[0]-1]]

        defx.action.do_action(self._vim, action, context)
