# ============================================================================
# FILE: filelike.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         Haruki Matsui <haru.matu9168 at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
from pynvim.api.common import NvimError
import shlex
import subprocess
import re
import time
import typing

from defx.action import ActionAttr
from defx.base.kind import Base, action
from defx.clipboard import ClipboardAction
from defx.context import Context
from defx.defx import Defx
from defx.util import cwd_input, confirm, error, Candidate
from defx.util import fnamemodify
from defx.view import View


PathLike = typing.Union[Path, typing.Any]


class Kind(Base):
    """ Abstract class which handles filelike objects kind.

    External kinds can inherit this class and use/override methods.
    """

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'filelike'

    def is_readable(self, path: PathLike) -> bool:
        pass

    def get_home(self) -> PathLike:
        pass

    def path_maker(self, path: str) -> PathLike:
        """
        Create PathLike object from string and returns it
        """
        pass

    def rmtree(self, path: PathLike) -> None:
        pass

    def get_buffer_name(self, path: str) -> str:
        '''
        Returns the buffer name when opening files in Vim buffer.
        Example:
             >>> self.get_buffer_name('/remote/path')
                ssh://usr@host/remote/path
        '''
        pass

    def paste(self, view: View, src: PathLike, dest: PathLike,
              cwd: str) -> None:
        pass

    def preview_file(self, view: View, defx: Defx,
                     context: Context, candidate: Candidate) -> None:
        filepath = str(candidate['action__path'])

        has_preview = bool(view._vim.call('defx#util#_get_preview_window'))
        if (has_preview and view._previewed_target and
                view._previewed_target == candidate):
            view._vim.command('pclose!')
            return

        prev_id = view._vim.call('win_getid')

        listed = view._vim.call('buflisted', filepath)

        view._previewed_target = candidate
        view._vim.call('defx#util#preview_file',
                       context._replace(targets=[])._asdict(),
                       self.get_buffer_name(filepath))
        view._vim.current.window.options['foldenable'] = False

        if not listed:
            bufnr = str(view._vim.call('bufnr', filepath))
            previewed_buffers = view._vim.vars['defx#_previewed_buffers']
            previewed_buffers[bufnr] = 1
            view._vim.vars['defx#_previewed_buffers'] = previewed_buffers

        view._vim.call('win_gotoid', prev_id)

    def input(self, view: View, defx: Defx, cwd: str, prompt: str, text: str,
              completion: str) -> str:
        if defx._source.name == 'file':
            res = cwd_input(
                view._vim, cwd,
                prompt, text, completion)
        else:
            res = str(view._vim.call(
                'defx#util#input',
                prompt, text, completion))
        return res

    def check_output(self, view: View, cwd: str,
                     args: typing.List[str]) -> None:
        output = subprocess.check_output(args, cwd=cwd)
        if output:
            view.print_msg(output)

    def check_overwrite(self, view: View,
                        dest: PathLike, src: PathLike) -> PathLike:
        if not src.exists() or not dest.exists():
            return self.path_maker('')

        s_stat = src.stat()
        s_mtime = s_stat.st_mtime
        view.print_msg(f' src: {src} {s_stat.st_size} bytes')
        view.print_msg(f'      {time.strftime("%c", time.localtime(s_mtime))}')
        d_stat = dest.stat()
        d_mtime = d_stat.st_mtime
        view.print_msg(f'dest: {dest} {d_stat.st_size} bytes')
        view.print_msg(f'      {time.strftime("%c", time.localtime(d_mtime))}')

        choice: int = view._vim.call(
            'defx#util#confirm',
            f'{dest} already exists.  Overwrite?',
            '&Force\n&No\n&Rename\n&Time\n&Underbar', 0)

        ret: PathLike = self.path_maker('')
        if choice == 1:
            ret = dest
        elif choice == 2:
            ret = self.path_maker('')
        elif choice == 3:
            ret = self.path_maker(view._vim.call(
                'defx#util#input',
                f'{src} -> ', str(dest),
                ('dir' if src.is_dir() else 'file')))
        elif choice == 4 and d_mtime < s_mtime:
            ret = src
        elif choice == 5:
            ret = self.path_maker(str(dest) + '_')
        return ret

    def execute_job(self, view: View, args: typing.List[str]) -> None:
        view._vim.call('defx#util#close_async_job')

        if view._vim.call('has', 'nvim'):
            jobfunc = 'jobstart'
            jobopts = {}
        else:
            jobfunc = 'job_start'
            jobopts = {'in_io': 'null', 'out_io': 'null', 'err_io': 'null'}

        view._vim.vars['defx#_async_job'] = view._vim.call(
            jobfunc, args, jobopts)

    def switch(self, view: View) -> None:
        windows = [x for x in range(1, view._vim.call('winnr', '$') + 1)
                   if view._vim.call('getwinvar', x, '&buftype') == '']

        result = view._vim.call('choosewin#start', windows,
                                {'auto_choose': True, 'hook_enable': False})
        if not result:
            # Open vertical
            view._vim.command('noautocmd rightbelow vnew')

    def create_open(self, view: View, defx: Defx, context: Context,
                    path: Path, command: str,
                    isdir: bool, isopen: bool) -> None:
        if isdir:
            path.mkdir(parents=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

        if not isopen:
            view.redraw(True)
            view.search_recursive(path, defx._index)
            return

        # Note: Must be redraw before actions
        view.redraw(True)
        view.search_recursive(path, defx._index)

        if isdir:
            if command == 'open_tree':
                view.open_tree(path, defx._index, False, 0)
            else:
                view.cd(defx, defx._source.name, str(path), context.cursor)
        else:
            if command == 'drop':
                self._drop(view, defx, context._replace(
                    args=[], targets=[{'action__path': path}]))
            else:
                view._vim.call('defx#util#execute_path',
                               command,
                               self.get_buffer_name(str(path)))

    @action(name='cd')
    def _cd(self, view: View, defx: Defx, context: Context) -> None:
        """
        Change the current directory.
        """
        source_name = defx._source.name
        is_parent = context.args and context.args[0] == '..'
        open = len(context.args) > 1 and context.args[1] == 'open'
        prev_cwd = self.path_maker(defx._cwd)

        if open:
            # Don't close current directory
            defx._opened_candidates.add(defx._cwd)

        if is_parent:
            path = prev_cwd.parent
        else:
            if context.args:
                if len(context.args) > 1:
                    source_name = context.args[0]
                    path = self.path_maker(context.args[1])
                else:
                    path = self.path_maker(context.args[0])
            else:
                path = self.get_home()
            path = prev_cwd.joinpath(path)
            if not self.is_readable(path):
                error(view._vim, f'{path} is invalid.')
            path = path.resolve()
            if source_name == 'file' and not path.is_dir():
                error(view._vim, f'{path} is invalid.')
                return

        view.cd(defx, source_name, str(path), context.cursor)
        if is_parent:
            view.search_file(prev_cwd, defx._index)

    @action(name='check_redraw', attr=ActionAttr.NO_TAGETS)
    def _check_redraw(self, view: View, defx: Defx, context: Context) -> None:
        root = defx.get_root_candidate()['action__path']
        if not root.exists():
            return
        mtime = root.stat().st_mtime
        if mtime != defx._mtime:
            view.redraw(True)

    @action(name='copy')
    def _copy(self, view: View, defx: Defx, context: Context) -> None:
        if not context.targets:
            return

        message = 'Copy to the clipboard: {}'.format(
            str(context.targets[0]['action__path'])
            if len(context.targets) == 1
            else str(len(context.targets)) + ' files')
        view.print_msg(message)

        view._clipboard.action = ClipboardAction.COPY
        view._clipboard.candidates = context.targets
        view._clipboard.source_name = defx._source.name

    @action(name='drop')
    def _drop(self, view: View, defx: Defx, context: Context) -> None:
        """
        Open like :drop.
        """
        cwd = view._vim.call('getcwd', -1)
        command = context.args[0] if context.args else 'edit'

        for target in context.targets:
            path = target['action__path']

            if path.is_dir():
                view.cd(defx, defx._source.name, str(path), context.cursor)
                continue

            # bufnr check
            winids = []
            try:
                bufnr = view._vim.call('bufnr', f'^{path}$')
                winids = view._vim.call('win_findbuf', bufnr)
            except NvimError:
                pass

            if winids:
                view._vim.call('win_gotoid', winids[0])
            else:
                # Jump to the last accessed window
                view._vim.command('wincmd p')

                if view._vim.call('win_getid') == view._winid:
                    view._vim.command('wincmd w')

                if (not view._vim.call('haslocaldir') and
                        not bool(view._vim.options['autochdir'])):
                    # Note: autochdir is dangerous option
                    try:
                        path = path.relative_to(cwd)
                    except ValueError:
                        pass

                view._vim.call('defx#util#execute_path', command,
                               self.get_buffer_name(str(path)))

            view.restore_previous_buffer(view._prev_bufnr)
        view.close_preview()

    @action(name='execute_command', attr=ActionAttr.REDRAW)
    def _execute_command(self, view: View, defx: Defx,
                         context: Context) -> None:
        """
        Execute the command.
        """

        command = (context.args[0]
                   if context.args and context.args[0]
                   else view._vim.call('defx#util#input',
                                       'Command: ', '', 'shellcmd'))
        if not command:
            return
        is_async = len(context.args) >= 2 and context.args[1] == 'async'

        view._vim.command('redraw')

        command_args = shlex.split(command)
        if '*' in command_args:
            args = []
            for arg in command_args:
                if arg == '*':
                    args += [str(x['action__path']) for x in context.targets]
                else:
                    args.append(arg)

            if is_async:
                self.execute_job(view, args)
            else:
                self.check_output(view, defx._cwd, args)
            return

        def parse_argument(arg: str) -> str:
            if not arg.startswith('%'):
                return arg
            arg = arg[1:]
            m = re.match(r'((:.)*)(.*)', arg)
            target_path = str(target['action__path'])
            if not m:
                return target_path
            return fnamemodify(view._vim, target_path, m.group(2)) + m.group(3)

        for target in context.targets:
            args = [parse_argument(x) for x in command_args]

            if is_async:
                self.execute_job(view, args)
            else:
                self.check_output(view, defx._cwd, args)

    @action(name='link')
    def _link(self, view: View, defx: Defx, context: Context) -> None:
        if not context.targets:
            return

        mode = context.args[0] if context.args else ''
        message = 'Link to the clipboard: {}'.format(
            str(context.targets[0]['action__path'])
            if len(context.targets) == 1
            else str(len(context.targets)) + ' files')
        view.print_msg(message)

        view._clipboard.action = ClipboardAction.LINK
        view._clipboard.candidates = context.targets
        view._clipboard.source_name = defx._source.name
        view._clipboard.mode = mode

    @action(name='move')
    def _move(self, view: View, defx: Defx, context: Context) -> None:
        if not context.targets:
            return

        message = 'Move to the clipboard: {}'.format(
            str(context.targets[0]['action__path'])
            if len(context.targets) == 1
            else str(len(context.targets)) + ' files')
        view.print_msg(message)

        view._clipboard.action = ClipboardAction.MOVE
        view._clipboard.candidates = context.targets
        view._clipboard.source_name = defx._source.name

    @action(name='new_directory', attr=ActionAttr.TREE)
    def _new_directory(self, view: View, defx: Defx, context: Context) -> None:
        """
        Create a new directory.
        """
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate:
            return

        if candidate['is_opened_tree'] or candidate['is_root']:
            cwd = str(candidate['action__path'])
        else:
            cwd = str(Path(candidate['action__path']).parent)

        new_filename = self.input(
            view, defx, cwd, 'Please input a new directory name: ', '', 'file')
        if not new_filename:
            return
        filename = self.path_maker(cwd).joinpath(new_filename)

        if not filename:
            return
        if filename.exists():
            error(view._vim, f'{filename} already exists')
            return

        isopen = len(context.args) > 0 and context.args[0] == 'open'
        command = context.args[1] if len(context.args) > 1 else 'edit'
        self.create_open(view, defx, context, filename, command, True, isopen)

    @action(name='new_file')
    def _new_file(self, view: View, defx: Defx, context: Context) -> None:
        """
        Create a new file and it's parent directories.
        """
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate:
            return

        if candidate['is_opened_tree'] or candidate['is_root']:
            cwd = str(candidate['action__path'])
        else:
            cwd = str(Path(candidate['action__path']).parent)

        new_filename = self.input(
            view, defx, cwd, 'Please input a new filename: ', '', 'file')
        if not new_filename:
            return
        isdir = new_filename[-1] == '/'
        filename = self.path_maker(cwd).joinpath(new_filename)

        if not filename:
            return
        if filename.exists():
            error(view._vim, f'{filename} already exists')
            return

        isopen = len(context.args) > 0 and context.args[0] == 'open'
        command = context.args[1] if len(context.args) > 1 else 'edit'
        self.create_open(view, defx, context, filename, command, isdir, isopen)

    @action(name='new_multiple_files', attr=ActionAttr.TREE)
    def _new_multiple_files(self, view: View, defx: Defx,
                            context: Context) -> None:
        """
        Create multiple files.
        """
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate:
            return

        if candidate['is_opened_tree'] or candidate['is_root']:
            cwd = str(candidate['action__path'])
        else:
            cwd = str(Path(candidate['action__path']).parent)

        isopen = len(context.args) > 0 and context.args[0] == 'open'
        command = context.args[1] if len(context.args) > 1 else 'edit'

        str_filenames = self.input(
            view, defx, cwd,
            'Please input new filenames: ', '', 'file')

        if not str_filenames:
            return None

        for name in shlex.split(str_filenames):
            isdir = name[-1] == '/'

            filename = self.path_maker(cwd).joinpath(name)
            if filename.exists():
                error(view._vim, f'{filename} already exists')
                continue

            self.create_open(view, defx, context,
                             filename, command, isdir, isopen)

    @action(name='open')
    def _open(self, view: View, defx: Defx, context: Context) -> None:
        """
        Open the file.
        """
        cwd = view._vim.call('getcwd', -1)
        command = context.args[0] if context.args else 'edit'
        choose = command == 'choose' and (
            view._vim.call('exists', 'g:loaded_choosewin')
            or view._vim.call('hasmapto', '<Plug>(choosewin)', 'n'))
        previewed_buffers = view._vim.vars['defx#_previewed_buffers']
        for target in context.targets:
            path = target['action__path']

            if path.is_dir():
                view.cd(defx, defx._source.name, str(path), context.cursor)
                continue

            if (not view._vim.call('haslocaldir') and
                    not bool(view._vim.options['autochdir'])):
                # Note: autochdir is dangerous option
                try:
                    path = path.relative_to(cwd)
                except ValueError:
                    pass

            if choose:
                self.switch(view)

            view._vim.call('defx#util#execute_path',
                           'edit' if choose else command,
                           self.get_buffer_name(str(path)))

            bufnr = str(view._vim.call('bufnr', str(path)))
            if bufnr in previewed_buffers:
                previewed_buffers.pop(bufnr)
                view._vim.vars['defx#_previewed_buffers'] = previewed_buffers

            view.restore_previous_buffer(view._prev_bufnr)
        view.close_preview()

    @action(name='open_directory')
    def _open_directory(self, view: View, defx: Defx,
                        context: Context) -> None:
        """
        Open the directory.
        """
        if context.args:
            path = self.path_maker(context.args[0])
        else:
            for target in context.targets:
                path = target['action__path']

        if path.is_dir():
            view.cd(defx, 'file', str(path), context.cursor)

    @action(name='paste', attr=ActionAttr.NO_TAGETS)
    def _paste(self, view: View, defx: Defx, context: Context) -> None:
        candidate = view.get_cursor_candidate(context.cursor)
        action = view._clipboard.action
        if not candidate or action == ClipboardAction.NONE:
            return

        if candidate['is_opened_tree'] or candidate['is_root']:
            cwd = str(candidate['action__path'])
        else:
            cwd = str(Path(candidate['action__path']).parent)

        dest = None
        for index, candidate in enumerate(view._clipboard.candidates):
            path = candidate['action__path']
            dest = self.path_maker(cwd).joinpath(path.name)
            if dest.exists():
                overwrite = self.check_overwrite(view, dest, path)
                if overwrite == self.path_maker(''):
                    continue
                dest = overwrite

            if not path.exists() or path == dest:
                continue

            view.print_msg(
                f'[{index + 1}/{len(view._clipboard.candidates)}] {path}')

            if dest.exists() and action != ClipboardAction.MOVE:
                # Must remove dest before
                if not dest.is_symlink() and dest.is_dir():
                    self.rmtree(dest)
                else:
                    dest.unlink()

            self.paste(view, path, dest, cwd)
            view._vim.command('redraw')

        if action == ClipboardAction.MOVE:
            # Clear clipboard after action
            view._clipboard.action = ClipboardAction.NONE
            view._clipboard.candidates = []

        view._vim.command('echo')

        view.redraw(True)
        if dest:
            view.search_recursive(dest, defx._index)

    @action(name='preview')
    def _preview(self, view: View, defx: Defx, context: Context) -> None:
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate or candidate['action__path'].is_dir():
            return

        self.preview_file(view, defx, context, candidate)

    @action(name='remove', attr=ActionAttr.REDRAW)
    def _remove(self, view: View, defx: Defx, context: Context) -> None:
        """
        Delete the file or directory.
        """
        if not context.targets:
            return

        force = context.args[0] == 'force' if context.args else False
        if not force:
            message = 'Are you sure you want to delete {}?'.format(
                str(context.targets[0]['action__path'])
                if len(context.targets) == 1
                else str(len(context.targets)) + ' files')
            if not confirm(view._vim, message):
                return

        for target in context.targets:
            path = target['action__path']

            if path.is_dir():
                self.rmtree(path)
            else:
                path.unlink()

            view._vim.call('defx#util#buffer_delete',
                           view._vim.call('bufnr', str(path)))

    @action(name='rename')
    def _rename(self, view: View, defx: Defx, context: Context) -> None:
        """
        Rename the file or directory.
        """

        if len(context.targets) > 1:
            # ex rename
            view._vim.call('defx#exrename#create_buffer',
                           [{'action__path': str(x['action__path'])}
                            for x in context.targets],
                           {'buffer_name': 'defx'})
            return

        mode = '' if not context.args else context.args[0]
        for target in context.targets:
            old = target['action__path']
            default = str(old)
            if mode == 'insert':
                view._vim.call('defx#util#back_cursor_input', len(old.name))
            elif mode == 'append':
                view._vim.call('defx#util#back_cursor_input', len(old.suffix))
            elif mode == 'new':
                default = default[: -len(old.name)]
            new_filename = self.input(
                view, defx, defx._cwd,
                f'Old name: {old}\nNew name: ', default, 'file')
            view._vim.command('redraw')
            if not new_filename:
                return
            new = self.path_maker(defx._cwd).joinpath(new_filename)
            if not new or new == old:
                continue
            if str(new).lower() != str(old).lower() and new.exists():
                error(view._vim, f'{new} already exists')
                continue

            if not new.parent.exists():
                new.parent.mkdir(parents=True)
            old.rename(new)

            # Check rename
            # The old is directory, the path may be matched opened file
            if not new.is_dir() and view._vim.call('bufexists', str(old)):
                view._vim.call('defx#util#buffer_rename',
                               view._vim.call('bufnr', str(old)), str(new))

            view.redraw(True)
            view.search_recursive(new, defx._index)
