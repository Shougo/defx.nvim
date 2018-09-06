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
    vim.call('defx#util#print_error', expr)


def cwd_input(vim: Nvim, cwd: str, prompt: str,
              text: str='', completion: str='') -> str:
    """
    Returns the absolute input path in cwd.
    """
    save_cwd = vim.call('getcwd')
    vim.command('silent lcd {}'.format(cwd))

    filename: str = vim.call('input', prompt, text, completion)
    filename = os.path.normpath(os.path.join(cwd, filename))

    vim.command('silent lcd {}'.format(save_cwd))
    return filename


def confirm(vim: Nvim, question: str) -> bool:
    """
    Confirm action
    """
    option: int = vim.call('confirm', question, '&Yes\n&No\n&Cancel')
    return option is 1
