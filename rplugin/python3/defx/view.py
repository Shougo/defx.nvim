# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from neovim import Nvim
import time
import typing
from pathlib import Path

from defx.base.column import Base as Column
from defx.clipboard import Clipboard
from defx.context import Context
from defx.defx import Defx
from defx.column.filename import Column as Filename
from defx.column.mark import Column as Mark
from defx.column.type import Column as Type
from defx.util import error


class View(object):

    def __init__(self, vim: Nvim, index: int) -> None:
        self._vim: Nvim = vim
        self._candidates: typing.List[dict] = []
        self._selected_candidates: typing.List[int] = []
        self._clipboard = Clipboard()
        self._bufnr = -1
        self._index = index
        self._bufname = '[defx]'

    def init(self, paths: typing.List[str], context: dict,
             clipboard: Clipboard) -> None:
        self._candidates = []
        self._selected_candidates = []
        self._context = Context(**context)
        self._clipboard = clipboard

        context['fnamewidth'] = int(context['fnamewidth'])
        context['winwidth'] = int(context['winwidth'])
        self._context = Context(**context)
        self._bufname = f'[defx] {self._context.buffer_name}-{self._index}'

        # Initialize defx
        self._defxs: typing.List[Defx] = []
        for [index, path] in enumerate(paths):
            self._defxs.append(Defx(self._vim, self._context, path, index))

        if not self.init_buffer():
            return

        # Initialize columns
        self._columns: typing.List[Column] = []
        self._all_columns: typing.Dict[str, Column] = {
            'mark': Mark(self._vim),
            'filename': Filename(self._vim),
            'type': Type(self._vim),
        }
        self._columns = [self._all_columns[x]
                         for x in self._context.columns.split(':')
                         if x in self._all_columns]
        start = 1
        for column in self._columns:
            column.on_init()
            column.start = start
            length = column.length(self._context)
            column.end = start + length - 1
            column.syntax_name = 'Defx_' + column.name
            start += length

        self.init_syntax()
        self.redraw(True)

        if self._context.search:
            for defx in self._defxs:
                if self.search_tree(self._context.search, defx._index):
                    break

    def init_buffer(self) -> bool:
        if self._context.split == 'tab':
            self._vim.command('tabnew')

        winnr = self._vim.call('bufwinnr', self._bufname)
        if (self._context.toggle and winnr > 0):
            self._vim.command(f'{winnr}wincmd w')
            self.quit()
            return False

        # Create new buffer
        self._vim.call(
            'defx#util#execute_path',
            'silent keepalt %s %s %s ' % (
                self._context.direction,
                ('vertical'
                 if self._context.split == 'vertical' else ''),
                ('edit'
                 if self._context.split == 'no' or
                 self._context.split == 'tab' else 'new'),
            ),
            self._bufname)

        if self._context.split == 'vertical' and self._context.winwidth > 0:
            self._vim.command(
                f'vertical resize {self._context.winwidth}')

        window_options = self._vim.current.window.options
        window_options['list'] = False
        window_options['wrap'] = False

        buffer_options = self._vim.current.buffer.options
        buffer_options['buftype'] = 'nofile'
        buffer_options['swapfile'] = False
        buffer_options['modeline'] = False
        buffer_options['filetype'] = 'defx'
        buffer_options['modifiable'] = False
        buffer_options['modified'] = False

        if not self._context.listed:
            buffer_options['buflisted'] = False
            buffer_options['bufhidden'] = 'wipe'

        self._vim.command('silent doautocmd FileType defx')
        self._vim.command('augroup defx | autocmd! | augroup END')
        self._vim.command('autocmd defx FocusGained <buffer> ' +
                          'call defx#_do_action("redraw", [])')
        self._bufnr = self._vim.current.buffer.number

        return True

    def init_syntax(self) -> None:
        for column in self._columns:
            self._vim.command(
                'silent! syntax clear ' + column.syntax_name)
            self._vim.command(
                'syntax region ' + column.syntax_name +
                ' start=/\%' + str(column.start) + 'v/ end=/\%' +
                str(column.end) + 'v/ keepend oneline')
            column.highlight()

    def debug(self, expr: typing.Any) -> None:
        error(self._vim, expr)

    def print_msg(self, expr: typing.Any) -> None:
        self._vim.call('defx#util#print_message', expr)

    def quit(self) -> None:
        if self._vim.call('winnr', '$') != 1:
            self._vim.command('close')
        else:
            self._vim.command('enew')

    def init_candidates(self) -> None:
        self._candidates = []
        for defx in self._defxs:
            candidates = [defx.get_root_candidate()]
            candidates += defx.gather_candidates()
            for candidate in candidates:
                candidate['_defx_index'] = defx._index
            self._candidates += candidates

    def redraw(self, is_force: bool = False) -> None:
        """
        Redraw defx buffer.
        """

        buffer_options = self._vim.current.buffer.options
        if buffer_options['filetype'] != 'defx':
            return

        start = time.time()

        prev = self.get_cursor_candidate(self._vim.call('line', '.'))

        if is_force:
            self._selected_candidates = []
            self.init_candidates()

        is_busy = time.time() - start > 0.5

        if is_busy:
            self.print_msg('Waiting...')

        # Set is_selected flag
        for candidate in self._candidates:
            candidate['is_selected'] = False
        for index in self._selected_candidates:
            self._candidates[index]['is_selected'] = True

        buffer_options['modifiable'] = True
        self._vim.current.buffer[:] = [
            self.get_columns_text(self._context, x)
            for x in self._candidates
        ]
        buffer_options['modifiable'] = False
        buffer_options['modified'] = False

        if prev:
            self.search_file(prev['action__path'], prev['_defx_index'])

        if is_busy:
            self._vim.command('redraw')
            self.print_msg('Done.')

        if self._context.profile:
            error(self._vim, f'redraw time = {time.time() - start}')

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

        global_histories = self._vim.vars['defx#_histories']
        global_histories.append(defx._cwd)
        self._vim.vars['defx#_histories'] = global_histories

        defx.cd(path)
        self.redraw(True)
        if path in history:
            self.search_file(history[path], defx._index)
        self._selected_candidates = []

    def search_tree(self, start: str, index: int) -> bool:
        path = Path(start)
        while True:
            if self.search_file(str(path), index):
                return True
            if path.parent == path:
                break
            path = path.parent
        return False

    def search_file(self, path: str, index: int) -> bool:
        linenr = 1
        for candidate in self._candidates:
            if (candidate['_defx_index'] == index and
                    str(candidate['action__path']) == path):
                self._vim.call('cursor', [linenr, 1])
                return True
            linenr += 1
        return False

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
            ret = action.do_action(self, defx, action_name, context)
            if ret:
                error(self._vim, 'Invalid action_name:' + action_name)
                return
