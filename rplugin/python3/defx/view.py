# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.defx import Defx


class View(object):

    def __init__(self, vim):
        self._vim = vim
        self._defx = Defx(self._vim)

    def redraw(self):
        self._vim.current.buffer[:] = [x['word'] for x in
                                       self._defx.gather_candidates()]
