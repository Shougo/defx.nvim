# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
import typing

from defx.source.file import Source as File
from defx.context import Context
from neovim import Nvim


class Defx(object):

    def __init__(self, vim: Nvim, cwd: str, index: int) -> None:
        self._vim = vim
        self._cwd = self._vim.call('getcwd')
        self.cd(cwd)
        self._source: File = File(self._vim)
        self._index = index

    def cd(self, path: str) -> None:
        path = os.path.normpath(os.path.join(self._cwd, path))
        self._cwd = path

    def get_root_candidate(self) -> dict:
        """
        Returns root candidate
        """
        root = self._source.get_root_candidate(Context(), self._cwd)
        root['is_root'] = True
        return root

    def gather_candidates(self) -> typing.List:
        """
        Returns file candidates
        """
        candidates = self._source.gather_candidates(Context(), self._cwd)

        # Sort
        dirs = sorted([x for x in candidates if x['is_directory']],
                      key=lambda x: x['abbr'])
        files = sorted([x for x in candidates if not x['is_directory']],
                       key=lambda x: x['abbr'])
        return dirs + files
