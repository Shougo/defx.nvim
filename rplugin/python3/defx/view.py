# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from defx.context import Context
from defx.defx import Defx
from neovim import Nvim


class View(object):

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._defx = Defx(self._vim, self._vim.call('getcwd'))

        # Create new buffer
        self._vim.call(
            'defx#util#execute_path',
            'silent keepalt edit', '[defx]')

        self._options = self._vim.current.buffer.options
        self._options['buftype'] = 'nofile'
        self._options['swapfile'] = False
        self._options['modeline'] = False
        self._options['filetype'] = 'defx'
        self._options['modifiable'] = False
        self._options['modified'] = False
        self._vim.command('silent doautocmd FileType defx')

    def redraw(self) -> None:
        """
        Redraw defx buffer.
        """
        self._candidates = self._defx.gather_candidates()
        self._options['modifiable'] = True
        self._vim.current.buffer[:] = [x['abbr'] for x in self._candidates]
        self._options['modifiable'] = False
        self._options['modified'] = False

    def do_action(self, action: str) -> None:
        """
        Do "action" action.
        """
        cursor = self._vim.current.window.cursor

        context = Context(targets=[self._candidates[cursor[0]-1]])

        import defx.action
        defx.action.do_action(self, self._defx, action, context)
