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

        if Defx.version_check():
            error(self._vim, 'Python 3.6.1+ is required.')

    def gather_candidates(self):
        f = File(self._vim)
        return f.gather_candidates({})

    @staticmethod
    def version_check():
        # Python version check
        # Python3.6.1+ is required.
        version = sys.version_info
        if version.major < 3:
            return True
        if version.major == 3 and version.minor < 6:
            return True
        if version.major == 3 and version.minor == 6 and version.micro < 1:
            return True

        return False
