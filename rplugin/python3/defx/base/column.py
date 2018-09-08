# ============================================================================
# FILE: column.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import abstractmethod

from defx.context import Context
from neovim import Nvim


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim: Nvim = vim
        self.name: str = 'base'
        self.syntax_name: str = ''
        self.start: int = -1
        self.end: int = -1
        self.vars: dict = {}

    def on_init(self) -> None:
        pass

    @abstractmethod
    def get(self, context: Context, candidate: dict) -> str:
        pass

    @abstractmethod
    def length(self, context: Context) -> int:
        pass

    def highlight(self) -> None:
        pass
