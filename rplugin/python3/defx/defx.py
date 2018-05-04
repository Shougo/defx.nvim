# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.source.file import Source as File


class Defx(object):

    def __init__(self, vim):
        self._vim = vim
        self._vim.vars['defx#_channel_id'] = self._vim.channel_id

    def gather_candidates(self):
        f = File(self._vim)
        return f.gather_candidates({})
