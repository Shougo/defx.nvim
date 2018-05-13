# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
from os.path import normpath, join


def abspath(vim, path):
    return normpath(join(vim.call('getcwd'), expand(path)))


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def error(vim, expr):
    if hasattr(vim, 'err_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        return vim.err_write('[defx] ' + string + '\n')
    else:
        vim.call('defx#util#print_error', expr)
