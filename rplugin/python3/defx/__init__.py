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
else:
    import pynvim
    vim = pynvim

Args = typing.List[typing.Any]

if hasattr(vim, 'plugin'):
    # Neovim only

    @vim.plugin
    class DefxHandlers:

        def __init__(self, vim: vim.Nvim) -> None:
            self._rplugin = Rplugin(vim)

        @vim.function('_defx_init', sync=True)  # type: ignore
        def init_channel(self, args: Args) -> None:
            self._rplugin.init_channel()

        @vim.rpc_export('_defx_start', sync=True)  # type: ignore
        def start(self, args: Args) -> None:
            self._rplugin.start(args)

        @vim.rpc_export('_defx_do_action', sync=True)  # type: ignore
        def do_action(self, args: Args) -> None:
            self._rplugin.do_action(args)

        @vim.rpc_export('_defx_async_action', sync=False)  # type: ignore
        def async_action(self, args: Args) -> None:
            self._rplugin.do_action(args)

        @vim.rpc_export('_defx_get_candidate', sync=True)  # type: ignore
        def get_candidate(self, args: Args
                          ) -> typing.Dict[str, typing.Union[str, bool]]:
            return self._rplugin.get_candidate()

if find_spec('yarp'):

    global_defx = Rplugin(vim)

    def _defx_init() -> None:
        pass

    def _defx_start(args: Args) -> None:
        global_defx.start(args)

    def _defx_do_action(args: Args) -> None:
        global_defx.do_action(args)

    def _defx_async_action(args: Args) -> None:
        global_defx.do_action(args)

    def _defx_get_candidate(args: Args
                            ) -> typing.Dict[str, typing.Union[str, bool]]:
        return global_defx.get_candidate()
