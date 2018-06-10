# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
import typing
from os.path import normpath, join

from neovim import Nvim


def abspath(vim: Nvim, path: str):
    return normpath(join(vim.call('getcwd'), expand(path)))


def expand(path: str):
    return os.path.expandvars(os.path.expanduser(path))


def error(vim: Nvim, expr: typing.Any):
    if hasattr(vim, 'err_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        return vim.err_write('[defx] ' + string + '\n')
    else:
        vim.call('defx#util#print_error', expr)
