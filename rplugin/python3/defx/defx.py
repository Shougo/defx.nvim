# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import sys

from defx.source.file import Source as File
from defx.util import error


class Defx(object):

    def __init__(self, vim):
        self._vim = vim
        self._vim.vars['defx#_channel_id'] = self._vim.channel_id

        # Python version check
        # Python3.6+ is required.
        if sys.version_info.major == 3 and sys.version_info.minor < 6:
            error(self._vim, 'Python 3.6+ is required.')

    def gather_candidates(self):
        f = File(self._vim)
        return f.gather_candidates({})
