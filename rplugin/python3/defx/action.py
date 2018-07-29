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
from defx.view import View


def do_action(view: View, defx: Defx, action_name: str, context: Context):
    """
    Do "action_name" action.
    """
    action = DEFAULT_ACTIONS[action_name]
    return action.func(view, defx, context)


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


class ActionAttr(IntFlag):
    REDRAW = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


DEFAULT_ACTIONS = {
    'open': ActionTable(func=_open),
}
