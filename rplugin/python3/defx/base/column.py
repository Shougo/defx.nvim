# ============================================================================
# FILE: column.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from abc import abstractmethod

from defx.context import Context
from defx.util import Nvim


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim: Nvim = vim
        self.name: str = 'base'
        self.syntax_name: str = ''
        self.start: int = -1
        self.end: int = -1
        self.vars: typing.Dict[str, typing.Any] = {}

    def on_init(self, context: Context) -> None:
        pass

    def on_redraw(self, context: Context) -> None:
        pass

    @abstractmethod
    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        pass

    @abstractmethod
    def length(self, context: Context) -> int:
        pass

    def syntaxes(self) -> typing.List[str]:
        return []

    def highlight_commands(self) -> typing.List[str]:
        return []
