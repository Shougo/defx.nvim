# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from importlib import find_loader
from defx.view import View
from neovim import Nvim


if find_loader('yarp'):
    import vim
else:
    import neovim
    vim = neovim

if 'neovim' in locals() and hasattr(neovim, 'plugin'):
    # Neovim only

    @neovim.plugin
    class DefxHandlers(object):

        def __init__(self, vim: Nvim) -> None:
            self._vim = vim

        @neovim.function('_defx_init')
        def init_channel(self, args: typing.List) -> None:
            self._vim.vars['defx#_channel_id'] = self._vim.channel_id

        @neovim.function('_defx_start')
        def start(self, args: typing.List) -> None:
            self._view = View(self._vim, args[0])
            self._view.redraw()

        @neovim.function('_defx_do_action')
        def do_action(self, args: typing.List) -> None:
            self._view.do_action(args[0], [])

if find_loader('yarp'):

    global_defx = View(vim, [])

    def defx_init() -> None:
        pass
