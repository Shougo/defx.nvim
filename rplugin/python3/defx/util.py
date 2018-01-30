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
