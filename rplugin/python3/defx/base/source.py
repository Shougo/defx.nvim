# ============================================================================
# FILE: source.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from abc import abstractmethod
from defx.context import Context
from defx.util import Nvim
from pathlib import Path


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'

        from defx.base.kind import Base as Kind
        self.kind: Kind = Kind(self.vim)

    @abstractmethod
    def gather_candidates(
            self, context: Context, path: Path
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        pass
