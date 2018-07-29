# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os

from defx.context import Context
from defx.defx import Defx
from defx.view import View


def _open(view: View, defx: Defx, context: Context):
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


def do_action(view: View, defx: Defx, action: str, context: Context):
    """
    Do "action" action.
    """
    return DEFAULT_ACTIONS[action](view, defx, context)


DEFAULT_ACTIONS = {
    'open': _open,
}
