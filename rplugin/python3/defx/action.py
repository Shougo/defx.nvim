# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os

from defx.context import Context
from neovim import Nvim


def _open(vim: Nvim, context: Context):
    """
    Open the file.
    """
    cwd = vim.call('getcwd')
    for target in context.targets:
        path = target['action__path']

        if path.startswith(cwd):
            path = os.path.relpath(path, cwd)

        vim.call(
            'defx#util#execute_path', 'edit', path)


def do_action(vim: Nvim, action: str, context: Context):
    """
    Do "action" action.
    """
    return DEFAULT_ACTIONS[action](vim, context)


DEFAULT_ACTIONS = {
    'open': _open,
}
