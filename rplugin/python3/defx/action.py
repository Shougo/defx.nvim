# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, IntFlag
import importlib
from pathlib import Path
import shutil
import time
import typing

from defx.clipboard import ClipboardAction
from defx.context import Context
from defx.defx import Defx
from defx.util import error, cwd_input, confirm, readable
from defx.view import View


def do_action(view: View, defx: Defx,
              action_name: str, context: Context) -> bool:
    """
    Do "action_name" action.
    """
    actions = DEFAULT_ACTIONS

    if action_name not in actions:
        return True

    action = actions[action_name]

    if ActionAttr.MARK not in action.attr and view._selected_candidates:
        # Clear marks
        view._selected_candidates = []
        view.redraw()

    action.func(view, defx, context)

    if action_name != 'repeat':
        view._prev_action = action_name

    if ActionAttr.MARK in action.attr:
        # Update marks
        view.redraw()
    elif ActionAttr.REDRAW in action.attr:
        # Redraw
        view.redraw(True)
    return False


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
        view.search_file(prev_cwd, defx._index)


def _change_vim_cwd(view: View, defx: Defx, context: Context) -> None:
    """
    Change the current working directory.
    """
    command = context.args[0] if context.args else 'lcd'
    view._vim.command(f'silent {command} {defx._cwd}')


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
    view.search_file(str(filename), defx._index)


def _new_file(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new file and it's parent directories.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new filename: ', '', 'file')
    if not filename:
        return
    if filename.exists():
        error(view._vim, '{filename} already exists')
        return

    if not filename.parent.exists():
        filename.parent.mkdir(parents=True)

    Path(filename).touch()

    view.redraw(True)
    view.search_file(str(filename), defx._index)


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
        view.search_file(str(dest), defx._index)


def _print(view: View, defx: Defx, context: Context) -> None:
    for target in context.targets:
        view.print_msg(str(target['action__path']))


def _repeat(view: View, defx: Defx, context: Context) -> None:
    do_action(view, defx, view._prev_action, context)


def _quit(view: View, defx: Defx, context: Context) -> None:
    view.quit()


def _redraw(view: View, defx: Defx, context: Context) -> None:
    view.redraw(True)
    if context.args and context.args[0]:
        view.search_tree(context.args[0], defx._index)


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
        view.search_file(str(new), defx._index)


def _toggle_select(view: View, defx: Defx, context: Context) -> None:
    index = context.cursor - 1
    if index in view._selected_candidates:
        view._selected_candidates.remove(index)
    else:
        view._selected_candidates.append(index)


def _toggle_select_all(view: View, defx: Defx, context: Context) -> None:
    for [index, candidate] in enumerate(view._candidates):
        if (not candidate.get('is_root', False) and
                candidate['_defx_index'] == defx._index):
            if index in view._selected_candidates:
                view._selected_candidates.remove(index)
            else:
                view._selected_candidates.append(index)


def _toggle_ignored_files(view: View, defx: Defx, context: Context) -> None:
    defx._enabled_ignored_files = not defx._enabled_ignored_files


def _yank_path(view: View, defx: Defx, context: Context) -> None:
    yank = '\n'.join([str(x['action__path']) for x in context.targets])
    view._vim.call('setreg', '"', yank)
    if (view._vim.call('has', 'clipboard') or
            view._vim.call('has', 'xterm_clipboard')):
        view._vim.call('setreg', '+', yank)
    view.print_msg('Yanked:\n' + yank)


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


class ActionAttr(IntFlag):
    REDRAW = auto()
    MARK = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


DEFAULT_ACTIONS = {
    'cd': ActionTable(func=_cd),
    'change_vim_cwd': ActionTable(func=_change_vim_cwd),
    'copy': ActionTable(func=_copy),
    'execute_command': ActionTable(func=_execute_command),
    'execute_system': ActionTable(func=_execute_system),
    'move': ActionTable(func=_move),
    'open': ActionTable(func=_open),
    'open_directory': ActionTable(func=_open_directory),
    'drop': ActionTable(func=_drop),
    'new_directory': ActionTable(func=_new_directory),
    'new_file': ActionTable(func=_new_file),
    'paste': ActionTable(func=_paste),
    'print': ActionTable(func=_print),
    'quit': ActionTable(func=_quit),
    'redraw': ActionTable(func=_redraw),
    'repeat': ActionTable(func=_repeat, attr=ActionAttr.MARK),
    'remove': ActionTable(func=_remove, attr=ActionAttr.REDRAW),
    'remove_trash': ActionTable(func=_remove_trash),
    'rename': ActionTable(func=_rename),
    'toggle_ignored_files': ActionTable(func=_toggle_ignored_files,
                                        attr=ActionAttr.REDRAW),
    'toggle_select': ActionTable(func=_toggle_select,
                                 attr=ActionAttr.MARK),
    'toggle_select_all': ActionTable(func=_toggle_select_all,
                                     attr=ActionAttr.MARK),
    'yank_path': ActionTable(func=_yank_path),
}
