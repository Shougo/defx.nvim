# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, IntFlag
import importlib
import os
from pathlib import Path
import shutil
import typing

from defx.context import Context
from defx.defx import Defx
from defx.util import error, cwd_input, confirm
from defx.view import View


def do_action(view: View, defx: Defx,
              action_name: str, context: Context) -> bool:
    """
    Do "action_name" action.
    """
    if action_name not in DEFAULT_ACTIONS:
        return True
    action = DEFAULT_ACTIONS[action_name]
    action.func(view, defx, context)
    if ActionAttr.REDRAW in action.attr:
        view.redraw(True)
    return False


def _cd(view: View, defx: Defx, context: Context) -> None:
    """
    Change the current directory.
    """
    path = Path(context.args[0]) if context.args else Path.home()
    path = path.joinpath(defx._cwd).resolve()
    if not path.is_dir():
        error(view._vim, '{} is not directory'.format(str(path)))
        return

    view.cd(defx, str(path), context.cursor)
    view._selected_candidates = []


def _new_directory(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new directory.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new directory: ', '', 'dir')
    if os.path.exists(filename):
        error(view._vim, '{} is already exists'.format(filename))
        return

    os.mkdir(filename)
    view.redraw(True)
    view.search_file(filename, defx._index)


def _new_file(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new file and it's parent directories.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new filename: ', '', 'file')
    if os.path.exists(filename):
        error(view._vim, '{} is already exists'.format(filename))
        return

    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    Path(filename).touch()

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

        if os.path.isdir(path):
            view.cd(defx, path, context.cursor)
        else:
            if path.startswith(cwd):
                path = os.path.relpath(path, cwd)
            view._vim.call('defx#util#execute_path', command, path)


def _print(view: View, defx: Defx, context: Context) -> None:
    for target in context.targets:
        view._vim.call('defx#util#print_debug', target['action__path'])


def _quit(view: View, defx: Defx, context: Context) -> None:
    view.quit()


def _redraw(view: View, defx: Defx, context: Context) -> None:
    pass


def _remove(view: View, defx: Defx, context: Context) -> None:
    """
    Delete the file or directory.
    """
    message = 'Are you sure you want to delete {}?'.format(
        context.targets[0]['action__path']
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    if not confirm(view._vim, message):
        return

    for target in context.targets:
        path = target['action__path']

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    view.redraw(True)


def _remove_trash(view: View, defx: Defx, context: Context) -> None:
    """
    Delete the file or directory.
    """
    if not importlib.find_loader('send2trash'):
        error(view._vim, '"Send2Trash" is not installed')
        return

    message = 'Are you sure you want to delete {}?'.format(
        context.targets[0]['action__path']
        if len(context.targets) == 1
        else str(len(context.targets)) + ' files')
    if not confirm(view._vim, message):
        return

    import send2trash
    for target in context.targets:
        send2trash.send2trash(target['action__path'])
    view.redraw(True)


def _rename(view: View, defx: Defx, context: Context) -> None:
    """
    Rename the file or directory.
    """
    for target in context.targets:
        path = target['action__path']
        filename = cwd_input(
            view._vim, defx._cwd,
            ('New name: {} -> '.format(path)), path, 'file')
        if not filename or filename == path:
            continue
        if os.path.exists(filename):
            error(view._vim, '{} is already exists'.format(filename))
            continue

        os.rename(path, filename)

        view.redraw(True)
        view.search_file(filename, defx._index)


def _toggle_select(view: View, defx: Defx, context: Context) -> None:
    index = context.cursor - 1
    if index in view._selected_candidates:
        view._selected_candidates.remove(index)
    else:
        view._selected_candidates.append(index)
    view.redraw()


def _toggle_select_all(view: View, defx: Defx, context: Context) -> None:
    for [index, candidate] in enumerate(view._candidates):
        if (not candidate.get('is_root', False) and
                candidate['_defx_index'] == defx._index):
            if index in view._selected_candidates:
                view._selected_candidates.remove(index)
            else:
                view._selected_candidates.append(index)
    view.redraw()


class ActionAttr(IntFlag):
    REDRAW = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


DEFAULT_ACTIONS = {
    'cd': ActionTable(func=_cd),
    'open': ActionTable(func=_open),
    'new_directory': ActionTable(func=_new_directory),
    'new_file': ActionTable(func=_new_file),
    'print': ActionTable(func=_print),
    'quit': ActionTable(func=_quit),
    'redraw': ActionTable(func=_redraw, attr=ActionAttr.REDRAW),
    'remove': ActionTable(func=_remove),
    'remove_trash': ActionTable(func=_remove_trash),
    'rename': ActionTable(func=_rename),
    'toggle_select': ActionTable(func=_toggle_select),
    'toggle_select_all': ActionTable(func=_toggle_select_all),
}
