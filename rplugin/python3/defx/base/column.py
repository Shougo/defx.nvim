# ============================================================================
# FILE: column.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing
from abc import abstractmethod

from defx.context import Context
from defx.util import error
from neovim import Nvim


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'
        self.syntax_name = ''
        self.start = -1
        self.end = -1

    def on_init(self) -> None:
        pass

    def debug(self, expr: typing.Any) -> None:
        error(self.vim, expr)

    @abstractmethod
    def get(self, context: Context, candidate: dict) -> str:
        pass

    @abstractmethod
    def length(self) -> int:
        pass

    def highlight(self) -> None:
        pass
