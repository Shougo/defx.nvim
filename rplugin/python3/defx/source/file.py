# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
import typing

from defx.base.source import Base
from defx.context import Context
from defx.util import error, readable, safe_call, Nvim


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'

    def get_root_candidate(self, context: Context, path: str) -> dict:
        return {
            'word': self.vim.call('fnamemodify',
                                  path + ('/' if path != '/' else ''), ':~'),
            'is_directory': True,
            'action__path': Path(path),
        }

    def gather_candidates(self, context: Context, path: Path) -> typing.List:
        candidates = []
        if not readable(path) or not path.is_dir():
            error(self.vim, f'"{path}" is not readable directory.')
            return []
        for entry in path.iterdir():
            candidates.append({
                'word': entry.name + ('/' if safe_call(entry.is_dir, False)
                                      else ''),
                'is_directory': safe_call(entry.is_dir, False),
                'action__path': entry,
            })
        return candidates
