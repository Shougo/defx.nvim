# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from importlib import find_loader
from defx.view import View


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
            self._defx = View(self._vim)
            self._defx.redraw()


if find_loader('yarp'):

    global_defx = View(vim)

    def defx_init():
        pass
