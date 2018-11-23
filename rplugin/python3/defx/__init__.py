# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from importlib.util import find_spec
from defx.rplugin import Rplugin


if find_spec('yarp'):
    import vim
elif find_spec('pynvim'):
    import pynvim
    vim = pynvim
else:
    import neovim
    vim = neovim

if hasattr(vim, 'plugin'):
    # Neovim only

    @vim.plugin
    class DefxHandlers:

        def __init__(self, vim: vim.Nvim) -> None:
            self._rplugin = Rplugin(vim)

        @vim.function('_defx_init', sync=True)  # type: ignore
        def init_channel(self, args: typing.List) -> None:
            self._rplugin.init_channel()

        @vim.function('_defx_start', sync=True)  # type: ignore
        def start(self, args: typing.List) -> None:
            self._rplugin.start(args)

        @vim.function('_defx_do_action', sync=True)  # type: ignore
        def do_action(self, args: typing.List) -> None:
            self._rplugin.do_action(args)

        @vim.function('_defx_async_action', sync=False)  # type: ignore
        def async_action(self, args: typing.List) -> None:
            self._rplugin.do_action(args)

if find_spec('yarp'):

    global_defx = Rplugin(vim)

    def _defx_init() -> None:
        pass

    def _defx_start(args: typing.List) -> None:
        global_defx.start(args)

    def _defx_do_action(args: typing.List) -> None:
        global_defx.do_action(args)

    def _defx_async_action(args: typing.List) -> None:
        global_defx.do_action(args)
