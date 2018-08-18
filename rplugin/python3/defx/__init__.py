# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from importlib import find_loader
from defx.rplugin import Rplugin


if find_loader('yarp'):
    import vim
else:
    import neovim
    vim = neovim

if 'neovim' in locals() and hasattr(neovim, 'plugin'):
    from neovim import Nvim
    # Neovim only

    @neovim.plugin
    class DefxHandlers:

        def __init__(self, vim: Nvim) -> None:
            self._rplugin = Rplugin(vim)

        @neovim.function('_defx_init', sync=True)  # type: ignore
        def init_channel(self, args: typing.List) -> None:
            self._rplugin.init_channel()

        @neovim.function('_defx_start', sync=True)  # type: ignore
        def start(self, args: typing.List) -> None:
            self._rplugin.start(args)

        @neovim.function('_defx_do_action', sync=True)  # type: ignore
        def do_action(self, args: typing.List) -> None:
            self._rplugin.do_action(args)

if find_loader('yarp'):

    global_defx = Rplugin(vim)

    def _defx_init() -> None:
        pass

    def _defx_start(args: typing.List) -> None:
        global_defx.start(args)

    def _defx_do_action(args: typing.List) -> None:
        global_defx.do_action(args)
