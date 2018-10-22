# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import os
import sys
import typing

from neovim import Nvim
from pathlib import Path

from importlib.machinery import SourceFileLoader


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


def import_plugin(path, source, classname):
    """Import defx plugin source class.

    If the class exists, add its directory to sys.path.
    """
    name = os.path.splitext(os.path.basename(path))[0]
    module_name = 'defx.%s.%s' % (source, name)

    module = SourceFileLoader(module_name, path).load_module()
    cls = getattr(module, classname, None)
    if not cls:
        return None

    dirname = os.path.dirname(path)
    if dirname not in sys.path:
        sys.path.insert(0, dirname)
    return cls
