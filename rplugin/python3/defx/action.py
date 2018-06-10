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
            match_path = '^{0}$'.format(path)

        if vim.call('bufwinnr', match_path) <= 0:
            vim.call(
                'defx#util#execute_path', 'edit', path)
        elif vim.call('bufwinnr',
                      match_path) != vim.current.buffer:
            vim.command('buffer' +
                        str(vim.call('bufnr', path)))


def do_action(vim: Nvim, action: str, context: Context):
    """
    Do "action" action.
    """
    return DEFAULT_ACTIONS[action](vim, context)


DEFAULT_ACTIONS = {
    'open': _open,
}
