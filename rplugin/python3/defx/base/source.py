# ============================================================================
# FILE: source.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from abc import abstractmethod
from defx.context import Context
from neovim import Nvim


class Base(object):

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'

    @abstractmethod
    def gather_candidate(self, context: Context) -> typing.List:
        pass
