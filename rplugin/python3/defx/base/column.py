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
        self.vim = vim
        self.name = 'base'
        self.syntax_name = ''

    @abstractmethod
    def get(self, context: Context, candidate: dict) -> str:
        pass
