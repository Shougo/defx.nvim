# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from importlib import find_loader
from defx.defx import Defx


if find_loader('yarp'):
    import vim
else:
    import neovim
    vim = neovim

if 'neovim' in locals() and hasattr(neovim, 'plugin'):
    # Neovim only

    @neovim.plugin
    class DefxHandlers(object):

        def __init__(self, vim):
            self._vim = vim

        @neovim.function('_defx_init', sync=False)
        def init_channel(self, args):
            self._defx = Defx(self._vim)


if find_loader('yarp'):

    global_defx = Defx(vim)

    def defx_init():
        pass
