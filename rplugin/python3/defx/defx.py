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
        v = sys.version_info
        return (v.major, v.minor, v.micro) < (3, 6, 1)
