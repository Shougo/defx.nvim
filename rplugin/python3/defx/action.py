# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, IntFlag
import os
import typing

from defx.context import Context
from defx.defx import Defx
from defx.util import error, cwd_input
from defx.view import View


def do_action(view: View, defx: Defx, action_name: str, context: Context):
    """
    Do "action_name" action.
    """
    action = DEFAULT_ACTIONS[action_name]
    action.func(view, defx, context)
    if ActionAttr.REDRAW in action.attr:
        view.redraw()


def _open(view: View, defx: Defx, context: Context) -> None:
    """
    Open the file.
    """
    cwd = view._vim.call('getcwd')
    for target in context.targets:
        path = target['action__path']

        if os.path.isdir(path):
            defx.cd(path)
            view.redraw()
        else:
            if path.startswith(cwd):
                path = os.path.relpath(path, cwd)
            view._vim.call('defx#util#execute_path', 'edit', path)


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


def _new_file(view: View, defx: Defx, context: Context) -> None:
    """
    Create a new file.
    """
    filename = cwd_input(view._vim, defx._cwd,
                         'Please input a new filename: ', '', 'file')
    if os.path.exists(filename):
        error(view._vim, '{} is already exists'.format(filename))
        return

    with open(filename, 'w') as f:
        f.write('')


class ActionAttr(IntFlag):
    REDRAW = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


DEFAULT_ACTIONS = {
    'open': ActionTable(func=_open),
    'new_directory': ActionTable(
        func=_new_directory, attr=ActionAttr.REDRAW),
    'new_file': ActionTable(
        func=_new_file, attr=ActionAttr.REDRAW),
}
