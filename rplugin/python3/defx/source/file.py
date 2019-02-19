# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import importlib
from pathlib import Path
import shutil
import time
import typing

from defx.action import ActionAttr
from defx.action import ActionTable
from defx.base.source import Base
from defx.clipboard import ClipboardAction
from defx.context import Context
from defx.defx import Defx
from defx.util import cwd_input, confirm, error
from defx.util import readable, safe_call, Nvim
from defx.view import View


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'
        self.actions = ACTIONS

    def get_root_candidate(
            self, context: Context, path: str
    ) -> typing.Dict[str, typing.Any]:
        return {
            'word': self.vim.call('fnamemodify',
                                  path + ('/' if path != '/' else ''), ':~'),
            'is_directory': True,
            'action__path': Path(path),
        }

    def gather_candidates(
            self, context: Context, path: Path
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        candidates = []
        if not readable(path) or not path.is_dir():
            error(self.vim, f'"{path}" is not readable directory.')
            return []
        for entry in path.iterdir():
            candidates.append({
                'word': entry.name + ('/' if safe_call(entry.is_dir, False)
                                      else ''),
                'is_directory': safe_call(entry.is_dir, False),
                'action__path': entry,
            })
        return candidates


def check_overwrite(view: View, dest: Path, src: Path) -> Path:
    s_stat = src.stat()
    s_mtime = s_stat.st_mtime
    view.print_msg(f' src: {src} {s_stat.st_size} bytes')
    view.print_msg(f'      {time.strftime("%c", time.localtime(s_mtime))}')
    d_stat = dest.stat()
    d_mtime = d_stat.st_mtime
    view.print_msg(f'dest: {dest} {d_stat.st_size} bytes')
    view.print_msg(f'      {time.strftime("%c", time.localtime(d_mtime))}')

    choice: int = view._vim.call('confirm',
                                 f'{dest} already exists.  Overwrite?',
                                 '&Force\n&No\n&Rename\n&Time\n&Underbar', 0)
    ret: Path = Path('')
    if choice == 1:
        ret = src
    elif choice == 2:
        ret = Path('')
    elif choice == 3:
        ret = Path(view._vim.call('input', f'{src} -> ', str(src),
                                  ('dir' if src.is_dir() else 'file')))
    elif choice == 4 and d_mtime < s_mtime:
        ret = src
    elif choice == 5:
        ret = Path(str(src) + '_')
    return ret


def _cd(view: View, defx: Defx, context: Context) -> None:
    """
    Change the current directory.
    """
    path = Path(context.args[0]) if context.args else Path.home()
    path = Path(defx._cwd).joinpath(path).resolve()
    if not readable(path) or not path.is_dir():
        error(view._vim, f'{path} is not readable directory')
        return

    prev_cwd = defx._cwd
    view.cd(defx, str(path), context.cursor)
    view._selected_candidates = []
    if context.args and context.args[0] == '..':
        view.search_file(Path(prev_cwd), defx._index)


def _change_vim_cwd(view: View, defx: Defx, context: Context) -> None:
    """
    Change the current working directory.
    """
    command = context.args[0] if context.args else 'lcd'
    view._vim.command(f'silent {command} {defx._cwd}')


def _check_redraw(view: View, defx: Defx, context: Context) -> None:
    root = defx.get_root_candidate()
    mtime = root['action__path'].stat().st_mtime
    if mtime != defx._mtime:
        view.redraw(True)


def _copy(view: View, defx: Defx, context: Context) -> None:
    if not context.targets:
        return

    message = 'Copy to the clipboard: {}'.format(
        str(context.targets[0]['action__path'])
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    view.print_msg(message)

    view._clipboard.action = ClipboardAction.COPY
    view._clipboard.candidates = context.targets


def _drop(view: View, defx: Defx, context: Context) -> None:
    """
    Open like :drop.
    """
    cwd = view._vim.call('getcwd')
    command = context.args[0] if context.args else 'edit'
    for target in context.targets:
        path = target['action__path']

        if path.is_dir():
            view.cd(defx, str(path), context.cursor)
            continue

        bufnr = view._vim.call('bufnr', str(path))
        winids = view._vim.call('win_findbuf', bufnr)

        if winids:
            view._vim.call('win_gotoid', winids[0])
        else:
            view._vim.command('wincmd p')
            if path.match(cwd):
                path = path.relative_to(cwd)
            view._vim.call('defx#util#execute_path', command, str(path))


def _execute_command(view: View, defx: Defx, context: Context) -> None:
    """
    Execute the command.
    """
    save_cwd = view._vim.call('getcwd')
    view._vim.command(f'silent lcd {defx._cwd}')

    command = context.args[0] if context.args else view._vim.call(
        'input', 'Command: ', '', 'shellcmd')

    output = view._vim.call('system', command)
    if output:
        view.print_msg(output)

    view._vim.command(f'silent lcd {save_cwd}')


def _execute_system(view: View, defx: Defx, context: Context) -> None:
    """
    Execute the file by system associated command.
    """
    for target in context.targets:
        view._vim.call('defx#util#open', str(target['action__path']))


def _move(view: View, defx: Defx, context: Context) -> None:
    if not context.targets:
        return

    message = 'Move to the clipboard: {}'.format(
        str(context.targets[0]['action__path'])
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    view.print_msg(message)

    view._clipboard.action = ClipboardAction.MOVE
    view._clipboard.candidates = context.targets


def _new_directory(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new directory.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new directory: ', '', 'dir')
    if not filename:
        return
    if filename.exists():
        error(view._vim, f'{filename} already exists')
        return

    filename.mkdir(parents=True)
    view.redraw(True)
    view.search_file(filename, defx._index)


def _new_file(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new file and it's parent directories.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new filename: ', '', 'file')
    if not filename:
        return
    if filename.exists():
        error(view._vim, f'{filename} already exists')
        return

    if not filename.parent.exists():
        filename.parent.mkdir(parents=True)

    filename.touch()

    view.redraw(True)
    view.search_file(filename, defx._index)


def _new_multiple_files(view: View, defx: Defx, context: Context) -> None:
    """
    Create multiple files.
    """

    save_cwd = view._vim.call('getcwd')
    view._vim.command(f'silent lcd {defx._cwd}')

    str_filenames: str = view._vim.call(
        'input', 'Please input new filenames: ', '', 'file')
    view._vim.command(f'silent lcd {save_cwd}')

    if not str_filenames:
        return None

    for name in str_filenames.split():
        is_dir = name[-1] == '/'

        filename = Path(defx._cwd).joinpath(name).resolve()
        if filename.exists():
            error(view._vim, f'{filename} already exists')
            continue

        if is_dir:
            filename.mkdir(parents=True)
        else:
            if not filename.parent.exists():
                filename.parent.mkdir(parents=True)
            filename.touch()

    view.redraw(True)
    view.search_file(filename, defx._index)


def _open(view: View, defx: Defx, context: Context) -> None:
    """
    Open the file.
    """
    cwd = view._vim.call('getcwd')
    command = context.args[0] if context.args else 'edit'
    for target in context.targets:
        path = target['action__path']

        if path.is_dir():
            view.cd(defx, str(path), context.cursor)
            continue

        if path.match(cwd):
            path = path.relative_to(cwd)
        view._vim.call('defx#util#execute_path', command, str(path))


def _open_directory(view: View, defx: Defx, context: Context) -> None:
    """
    Open the directory.
    """
    for target in context.targets:
        path = target['action__path']

        if path.is_dir():
            view.cd(defx, str(path), context.cursor)


def _paste(view: View, defx: Defx, context: Context) -> None:
    action = view._clipboard.action
    dest = None
    for index, candidate in enumerate(view._clipboard.candidates):
        path = candidate['action__path']
        dest = Path(defx._cwd).joinpath(path.name)
        if dest.exists():
            overwrite = check_overwrite(view, dest, path)
            if overwrite == Path(''):
                continue
            dest = Path(defx._cwd).joinpath(overwrite.name)

        if path == dest:
            continue

        view.print_msg(
            f'[{index + 1}/{len(view._clipboard.candidates)}] {path}')
        if action == ClipboardAction.COPY:
            if path.is_dir():
                shutil.copytree(str(path), dest)
            else:
                shutil.copy2(str(path), dest)
        elif action == ClipboardAction.MOVE:
            shutil.move(str(path), defx._cwd)
        view._vim.command('redraw')
    view._vim.command('echo')

    view.redraw(True)
    if dest:
        view.search_file(dest, defx._index)


def _remove(view: View, defx: Defx, context: Context) -> None:
    """
    Delete the file or directory.
    """
    if not context.targets:
        return

    message = 'Are you sure you want to delete {}?'.format(
        str(context.targets[0]['action__path'])
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    if not confirm(view._vim, message):
        return

    for target in context.targets:
        path = target['action__path']

        if path.is_dir():
            shutil.rmtree(str(path))
        else:
            path.unlink()


def _remove_trash(view: View, defx: Defx, context: Context) -> None:
    """
    Delete the file or directory.
    """
    if not context.targets:
        return

    if not importlib.util.find_spec('send2trash'):
        error(view._vim, '"Send2Trash" is not installed')
        return

    message = 'Are you sure you want to delete {}?'.format(
        str(context.targets[0]['action__path'])
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    if not confirm(view._vim, message):
        return

    import send2trash
    for target in context.targets:
        send2trash.send2trash(str(target['action__path']))
    view.redraw(True)


def _rename(view: View, defx: Defx, context: Context) -> None:
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

    for target in context.targets:
        old = target['action__path']
        new = cwd_input(
            view._vim, defx._cwd, f'New name: {old} -> ', str(old), 'file')
        if not new or new == old:
            continue
        if new.exists():
            error(view._vim, f'{new} already exists')
            continue

        old.rename(new)

        view.redraw(True)
        view.search_file(new, defx._index)


ACTIONS = {
    'cd': ActionTable(func=_cd),
    'change_vim_cwd': ActionTable(func=_change_vim_cwd),
    'check_redraw': ActionTable(func=_check_redraw),
    'copy': ActionTable(func=_copy),
    'drop': ActionTable(func=_drop),
    'execute_command': ActionTable(func=_execute_command),
    'execute_system': ActionTable(func=_execute_system),
    'move': ActionTable(func=_move),
    'new_directory': ActionTable(func=_new_directory),
    'new_file': ActionTable(func=_new_file),
    'new_multiple_files': ActionTable(func=_new_multiple_files),
    'open': ActionTable(func=_open),
    'open_directory': ActionTable(func=_open_directory),
    'paste': ActionTable(func=_paste),
    'remove': ActionTable(func=_remove, attr=ActionAttr.REDRAW),
    'remove_trash': ActionTable(func=_remove_trash),
    'rename': ActionTable(func=_rename),
}
