# ============================================================================
# FILE: rplugin.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from defx.view import View
from neovim import Nvim


class Rplugin:

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim

    def init_channel(self, args: typing.List) -> None:
        self._vim.vars['defx#_channel_id'] = self._vim.channel_id

    def start(self, args: typing.List) -> None:
        self._view = View(self._vim, args[0], args[1])
        self._view.redraw()

    def do_action(self, args: typing.List) -> None:
        self._view.do_action(args[0], args[1], args[2])
