# ============================================================================
# FILE: defx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import typing

from defx.source.file import Source as File
from defx.context import Context
from defx.util import Nvim
from pathlib import Path


class Defx(object):

    def __init__(self, vim: Nvim, context: Context,
                 cwd: str, index: int) -> None:
        self._vim = vim
        self._context = context
        self._cwd = self._vim.call('getcwd')
        self.cd(cwd)
        self._source: File = File(self._vim)
        self._index = index
        self._enabled_ignored_files = True
        self._ignored_files = ['.*']
        self._cursor_history: typing.Dict[str, str] = {}

    def cd(self, path: str) -> None:
        self._cwd = str(Path(self._cwd).joinpath(path).resolve())

        if self._context.auto_cd:
            self._vim.command('silent lcd ' + path)

    def get_root_candidate(self) -> dict:
        """
        Returns root candidate
        """
        root = self._source.get_root_candidate(self._context, self._cwd)
        root['is_root'] = True
        return root

    def gather_candidates(self, path: str = '') -> typing.List:
        """
        Returns file candidates
        """
        if not path:
            path = self._cwd

        candidates = self._source.gather_candidates(
            self._context, Path(path))

        if self._enabled_ignored_files:
            for glob in self._ignored_files:
                candidates = [x for x in candidates
                              if not x['action__path'].match(glob)]

        pattern = re.compile(r'(\d+)')

        def numeric_key(v: str) -> typing.List[typing.Any]:
            keys = pattern.split(v)
            keys[1::2] = [int(x) for x in keys[1::2]]  # type: ignore
            return keys

        # Sort
        dirs = sorted([x for x in candidates if x['is_directory']],
                      key=lambda x: numeric_key(x['word']))
        files = sorted([x for x in candidates if not x['is_directory']],
                       key=lambda x: numeric_key(x['word']))
        return dirs + files
