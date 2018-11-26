# ============================================================================
# FILE: view.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import time
import typing
from pathlib import Path

from defx.base.column import Base as Column
from defx.clipboard import Clipboard
from defx.context import Context
from defx.defx import Defx
from defx.util import error, import_plugin, safe_call, Nvim


class View(object):

    def __init__(self, vim: Nvim, index: int) -> None:
        self._vim: Nvim = vim
        self._candidates: typing.List[dict] = []
        self._selected_candidates: typing.List[int] = []
        self._clipboard = Clipboard()
        self._bufnr = -1
        self._index = index
        self._bufname = '[defx]'
        self._buffer: Nvim.buffer = None
        self._prev_action = ''

    def init(self, paths: typing.List[str], context: dict,
             clipboard: Clipboard) -> None:
        context['fnamewidth'] = int(context['fnamewidth'])
        context['winheight'] = int(context['winheight'])
        context['winwidth'] = int(context['winwidth'])
        context['prev_bufnr'] = int(context['prev_bufnr'])
        self._context = Context(**context)
        self._bufname = f'[defx] {self._context.buffer_name}-{self._index}'

        if not self.init_buffer():
            return

        self._candidates = []
        self._selected_candidates = []
        self._context = Context(**context)
        self._clipboard = clipboard

        # Initialize defx
        self._defxs: typing.List[Defx] = []
        for [index, path] in enumerate(paths):
            self._defxs.append(Defx(self._vim, self._context, path, index))

        self.init_columns()
        self.init_syntax()

        if self._context.search:
            for defx in self._defxs:
                if self.search_tree(self._context.search, defx._index):
                    break

    def init_columns(self) -> None:
        # Initialize columns
        self._columns: typing.List[Column] = []
        self._all_columns: typing.Dict[str, Column] = {}

        for path_column in self.load_custom_columns():
            column = import_plugin(path_column, 'column', 'Column')
            if not column:
                continue

            column = column(self._vim)
            if column.name not in self._all_columns:
                self._all_columns[column.name] = column

        self._columns = [self._all_columns[x]
                         for x in self._context.columns.split(':')
                         if x in self._all_columns]
        for column in self._columns:
            column.on_init(self._context)
            column.syntax_name = 'Defx_' + column.name

    def init_buffer(self) -> bool:
        if self._context.split == 'tab':
            self._vim.command('tabnew')

        winnr = self._vim.call('bufwinnr', self._bufname)
        if winnr > 0:
            self._vim.command(f'{winnr}wincmd w')
            if self._context.toggle:
                self.quit()
                return False
            return True

        # Create new buffer
        vertical = 'vertical' if self._context.split == 'vertical' else ''
        if self._vim.call('bufexists', self._bufnr):
            command = ('buffer' if self._context.split in ['no', 'tab']
                       else 'sbuffer')
            self._vim.command(
                'silent keepalt %s %s %s %s' % (
                    self._context.direction,
                    vertical,
                    command,
                    self._bufnr,
                )
            )
            if self._context.resume:
                return False
        else:
            command = ('edit' if self._context.split in ['no', 'tab']
                       else 'new')
            self._vim.call(
                'defx#util#execute_path',
                'silent keepalt %s %s %s ' % (
                    self._context.direction,
                    vertical,
                    command,
                ),
                self._bufname)

        self._buffer = self._vim.current.buffer
        self._bufnr = self._buffer.number

        window_options = self._vim.current.window.options
        window_options['list'] = False
        window_options['wrap'] = False

        if (self._context.split == 'vertical'
                and self._context.winwidth > 0):
            window_options['winfixwidth'] = True
            self._vim.command(f'vertical resize {self._context.winwidth}')
        elif (self._context.split == 'horizontal' and
              self._context.winheight > 0):
            window_options['winfixheight'] = True
            self._vim.command(f'resize {self._context.winheight}')

        buffer_options = self._buffer.options
        buffer_options['buftype'] = 'nofile'
        buffer_options['swapfile'] = False
        buffer_options['modeline'] = False
        buffer_options['filetype'] = 'defx'
        buffer_options['modifiable'] = False
        buffer_options['modified'] = False

        self._buffer.vars['defx'] = {
            'context': self._context._asdict(),
        }

        if not self._context.listed:
            buffer_options['buflisted'] = False
            buffer_options['bufhidden'] = 'wipe'

        self._vim.command('silent doautocmd FileType defx')
        self._vim.command('autocmd! FocusGained <buffer>')
        self._vim.command('autocmd defx FocusGained <buffer> ' +
                          'call defx#_async_action("redraw", [])')

        return True

    def init_syntax(self) -> None:
        start = 1
        for column in self._columns:
            column.start = start
            length = column.length(self._context)
            column.end = start + length

            self._vim.command(
                'silent! syntax clear ' + column.syntax_name)
            self._vim.command(
                'syntax region ' + column.syntax_name +
                r' start=/\%' + str(column.start) + r'v/ end=/\%' +
                str(column.end) + 'v/ keepend oneline')
            column.highlight()

            start += length + 1

    def debug(self, expr: typing.Any) -> None:
        error(self._vim, expr)

    def print_msg(self, expr: typing.Any) -> None:
        self._vim.call('defx#util#print_message', expr)

    def quit(self) -> None:
        if self._context.split in ['no', 'tab']:
            if self._vim.call('bufexists', self._context.prev_bufnr):
                self._vim.command('buffer ' + str(self._context.prev_bufnr))
            else:
                self._vim.command('enew')
        else:
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

        if self._buffer != self._vim.current.buffer:
            return

        start = time.time()

        prev = self.get_cursor_candidate(self._vim.call('line', '.'))

        if is_force:
            self._selected_candidates = []
            self.init_candidates()

        # Set is_selected flag
        for candidate in self._candidates:
            candidate['is_selected'] = False
        for index in self._selected_candidates:
            self._candidates[index]['is_selected'] = True

        for column in self._columns:
            column.on_redraw(self._context)

        if self._buffer != self._vim.current.buffer:
            return

        self._buffer.options['modifiable'] = True
        self._buffer[:] = [
            self.get_columns_text(self._context, x)
            for x in self._candidates
        ]
        self._buffer.options['modifiable'] = False
        self._buffer.options['modified'] = False

        if prev:
            self.search_file(prev['action__path'], prev['_defx_index'])

        if self._context.profile:
            error(self._vim, f'redraw time = {time.time() - start}')

    def get_columns_text(self, context: Context, candidate: dict) -> str:
        text = ''
        for column in self._columns:
            if text:
                text += ' '
            text += column.get(context, candidate)
        return text

    def get_cursor_candidate(self, cursor: int) -> dict:
        if len(self._candidates) < cursor:
            return {}
        else:
            return self._candidates[cursor - 1]

    def get_selected_candidates(
            self, cursor: int, index: int) -> typing.List[dict]:
        if not self._candidates:
            return []
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
        cursor = new_context['cursor']

        defx_targets = {
            x._index: self.get_selected_candidates(cursor, x._index)
            for x in self._defxs}

        import defx.action as action
        for defx in self._defxs:
            context = self._context._replace(
                targets=defx_targets[defx._index],
                args=action_args,
                cursor=cursor
            )
            ret = action.do_action(self, defx, action_name, context)
            if ret:
                error(self._vim, 'Invalid action_name:' + action_name)
                return

    def load_custom_columns(self) -> typing.List[Path]:
        rtp_list = self._vim.options['runtimepath'].split(',')
        result: typing.List[Path] = []

        for path in rtp_list:
            column_path = Path(path).joinpath(
                'rplugin', 'python3', 'defx', 'column')
            if safe_call(column_path.is_dir):
                result += column_path.glob('*.py')

        return result
