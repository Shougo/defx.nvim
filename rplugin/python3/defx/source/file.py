# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import glob
import os
import typing

from .base import Base
from defx.context import Context
from defx.util import abspath
from neovim import Nvim


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'

    def gather_candidates(self, context: Context) -> typing.List:
        candidates = []
        for f in glob.glob('.*'):
            candidates.append({
                'word': f,
                'abbr': f + ('/' if os.path.isdir(f) else ''),
                'kind': ('directory' if os.path.isdir(f) else 'file'),
                'is_directory': os.path.isdir(f),
                'action__path': abspath(self.vim, f),
            })
        return candidates
