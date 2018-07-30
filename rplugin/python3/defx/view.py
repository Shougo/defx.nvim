# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from neovim import Nvim
import typing

from defx.context import Context
from defx.defx import Defx


class View(object):

    def __init__(self, vim: Nvim, paths: typing.List[str]) -> None:
        self._vim: Nvim = vim
        # Initialize defx
        self._defxs: typing.List[Defx] = []
        for path in paths:
            self._defxs.append(Defx(self._vim, path))
        self._candidates: typing.List = []
        self._selected_candidates: typing.List = []

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
        self._candidates = []
        for defx in self._defxs:
            self._candidates.append({
                'word': defx._cwd,
                'abbr': defx._cwd + '/',
                'kind': 'directory',
                'is_directory': True,
                'is_root': True,
                'action__path': defx._cwd,
            })
            self._candidates += defx.gather_candidates()
        self._options['modifiable'] = True
        self._vim.current.buffer[:] = [x['abbr'] for x in self._candidates]
        self._options['modifiable'] = False
        self._options['modified'] = False

    def get_selected_candidates(self) -> typing.List[dict]:
        cursor = self._vim.current.window.cursor
        return [self._candidates[cursor[0]-1]]

    def do_action(self, action_name: str,
                  action_args: typing.List[str]) -> None:
        """
        Do "action" action.
        """
        if not self._candidates:
            return

        context = Context(
            targets=self.get_selected_candidates(),
            args=action_args
        )

        import defx.action as action
        for defx in self._defxs:
            action.do_action(self, defx, action_name, context)
