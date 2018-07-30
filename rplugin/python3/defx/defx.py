# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
import sys
import typing

from defx.source.file import Source as File
from defx.context import Context
from defx.util import error
from neovim import Nvim


class Defx(object):

    def __init__(self, vim: Nvim, cwd: str) -> None:
        self._vim = vim
        self._cwd = self._vim.call('getcwd')
        self.cd(cwd)

        if Defx.version_check():
            error(self._vim, 'Python 3.6.1+ is required.')

    def cd(self, path: str) -> None:
        path = os.path.normpath(os.path.join(self._cwd, path))
        self._cwd = path

    def gather_candidates(self) -> typing.List:
        """
        Returns file candidates
        """
        f = File(self._vim)  # type: ignore
        candidates = f.gather_candidates(Context(), self._cwd)

        # Sort
        dirs = sorted([x for x in candidates if x['is_directory']],
                      key=lambda x: x['abbr'])
        files = sorted([x for x in candidates if not x['is_directory']],
                       key=lambda x: x['abbr'])
        return dirs + files

    @staticmethod
    def version_check() -> bool:
        """
        Checks Python version.
        Python3.6.1+ is required for defx.
        """
        v = sys.version_info
        return (v.major, v.minor, v.micro) < (3, 6, 1)
