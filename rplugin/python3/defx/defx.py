# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import sys
import typing

from defx.source.file import Source as File
from defx.context import Context
from defx.util import error
from neovim import Nvim


class Defx(object):

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._vim.vars['defx#_channel_id'] = self._vim.channel_id

        if Defx.version_check():
            error(self._vim, 'Python 3.6.1+ is required.')

    def gather_candidates(self) -> typing.List:
        """
        Returns file candidates
        """
        f = File(self._vim)  # type: ignore
        return f.gather_candidates(Context(targets=[]))

    @staticmethod
    def version_check() -> bool:
        """
        Checks Python version.
        Python3.6.1+ is required for defx.
        """
        version = sys.version_info
        if version.major < 3:
            return True
        if version.major == 3 and version.minor < 6:
            return True
        if version.major == 3 and version.minor == 6 and version.micro < 1:
            return True

        return False
