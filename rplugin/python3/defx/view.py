# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from neovim import Nvim
import typing

from defx.base.column import Base as Column
from defx.context import Context
from defx.defx import Defx
from defx.column.filename import Column as Filename
from defx.column.mark import Column as Mark
from defx.util import error


class View(object):

    def __init__(self, vim: Nvim,
                 paths: typing.List[str], context: dict) -> None:
        self._vim: Nvim = vim
        self._candidates: typing.List[dict] = []
        self._selected_candidates: typing.List[int] = []
        self._context = Context(**context)

        # Initialize defx
        self._defxs: typing.List[Defx] = []
        index = 0
        for path in paths:
            self._defxs.append(Defx(self._vim, self._context, path, index))
            index += 1

        self.init_buffer()

        # Initialize columns
        self._columns: typing.List[Column] = []
        for column in [Mark(self._vim), Filename(self._vim)]:
            column.syntax_name = 'Defx_' + column.name
            self._columns.append(column)

        self.init_syntax()

    def init_buffer(self) -> None:
        # Create new buffer
        self._vim.call(
            'defx#util#execute_path',
            'silent keepalt edit', '[defx]')

        self._vim.current.window.options['list'] = False
        self._vim.current.window.options['wrap'] = False
        self._options = self._vim.current.buffer.options
        self._options['buftype'] = 'nofile'
        self._options['swapfile'] = False
        self._options['modeline'] = False
        self._options['filetype'] = 'defx'
        self._options['modifiable'] = False
        self._options['modified'] = False
        self._options['buflisted'] = False
        self._options['bufhidden'] = 'wipe'
        self._vim.command('silent doautocmd FileType defx')
        self._vim.command('augroup defx | autocmd! | augroup END')
        self._vim.command('autocmd defx FocusGained <buffer> ' +
                          'call defx#_do_action("redraw", [])')

    def init_syntax(self) -> None:
        start = 1
        for column in self._columns:
            self._vim.command(
                'silent! syntax clear ' + column.syntax_name)
            self._vim.command(
                'syntax region ' + column.syntax_name +
                ' start=/\%' + str(start) + 'v/ end=/\%' +
                str(start + column.length() - 1) + 'v/ keepend oneline')
            column.highlight()
            start += column.length()

    def debug(self, expr: typing.Any) -> None:
        error(self._vim, expr)

    def redraw(self, is_force: bool = False) -> None:
        """
        Redraw defx buffer.
        """

        if is_force:
            self._selected_candidates = []

        prev = self.get_cursor_candidate(self._vim.call('line', '.'))

        self._candidates = []
        for defx in self._defxs:
            candidates = [defx.get_root_candidate()]
            candidates += defx.gather_candidates()
            for candidate in candidates:
                candidate['_defx_index'] = defx._index
            self._candidates += candidates

        # Set is_selected flag
        for index in self._selected_candidates:
            self._candidates[index]['is_selected'] = True

        self._options['modifiable'] = True
        self._vim.current.buffer[:] = [
            self.get_columns_text(self._context, x)
            for x in self._candidates
        ]
        self._options['modifiable'] = False
        self._options['modified'] = False

        if prev:
            self.search_file(prev['action__path'], prev['_defx_index'])

    def get_columns_text(self, context: Context, candidate: dict) -> str:
        text = ''
        for column in self._columns:
            text += column.get(context, candidate)
        return text

    def get_cursor_candidate(self, cursor: int) -> dict:
        if len(self._candidates) < cursor:
            return {}
        else:
            return self._candidates[cursor - 1]

    def get_selected_candidates(
            self, cursor: int, index: int) -> typing.List[dict]:
        if not self._selected_candidates:
            candidates = [self.get_cursor_candidate(cursor)]
        else:
            candidates = [self._candidates[x]
                          for x in self._selected_candidates]
        return [x for x in candidates if x['_defx_index'] == index]

    def cd(self, defx: Defx, path: str, cursor: int) -> None:
        # Save previous cursor position
        history = defx._cursor_history
        history[defx._cwd] = self.get_cursor_candidate(cursor)['action__path']

        defx.cd(path)
        self.redraw(True)
        if path in history:
            self.search_file(history[path], defx._index)
        self._selected_candidates = []

    def search_file(self, path: str, index: int) -> None:
        linenr = 1
        for candidate in self._candidates:
            if (candidate['_defx_index'] == index and
                    candidate['action__path'] == path):
                self._vim.call('cursor', [linenr, 1])
                return
            linenr += 1

    def do_action(self, action_name: str,
                  action_args: typing.List[str], new_context: dict) -> None:
        """
        Do "action" action.
        """
        if not self._candidates:
            return

        cursor = new_context['cursor']

        import defx.action as action
        for defx in self._defxs:
            targets = self.get_selected_candidates(cursor, defx._index)
            if not targets:
                continue
            context = self._context._replace(
                targets=targets,
                args=action_args,
                cursor=cursor
            )
            action.do_action(self, defx, action_name, context)
