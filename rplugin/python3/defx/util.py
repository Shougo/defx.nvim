# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from neovim import Nvim
from pathlib import Path


def error(vim: Nvim, expr: typing.Any) -> None:
    """
    Prints the error messages to Vim/Nvim's :messages buffer.
    """
    vim.call('defx#util#print_error', expr)


def cwd_input(vim: Nvim, cwd: str, prompt: str,
              text: str = '', completion: str = '') -> typing.Optional[Path]:
    """
    Returns the absolute input path in cwd.
    """
    save_cwd = vim.call('getcwd')
    vim.command(f'silent lcd {cwd}')

    filename: str = vim.call('input', prompt, text, completion)
    if not filename:
        return None

    vim.command(f'silent lcd {save_cwd}')
    return Path(cwd).joinpath(filename).resolve()


def confirm(vim: Nvim, question: str) -> bool:
    """
    Confirm action
    """
    option: int = vim.call('confirm', question, '&Yes\n&No\n&Cancel')
    return option is 1
