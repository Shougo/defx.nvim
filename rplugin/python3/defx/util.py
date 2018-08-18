# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
import typing

from neovim import Nvim


def expand(path: str) -> str:
    """
    Expands the path.
    """
    return os.path.expandvars(os.path.expanduser(path))


def error(vim: Nvim, expr: typing.Any) -> None:
    """
    Prints the error messages to Vim/Nvim's :messages buffer.
    """
    if hasattr(vim, 'err_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        vim.err_write('[defx] ' + string + '\n')
    else:
        vim.call('defx#util#print_error', expr)


def cwd_input(vim: Nvim, cwd: str, prompt: str,
              text: str='', completion: str='') -> str:
    """
    Returns the absolute input path in cwd.
    """
    save_cwd = vim.call('getcwd')
    vim.command('lcd {}'.format(cwd))

    filename: str = vim.call('input', prompt, text, completion)
    filename = os.path.normpath(os.path.join(cwd, filename))

    vim.command('lcd {}'.format(save_cwd))
    return filename
