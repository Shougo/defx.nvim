# ============================================================================
# FILE: context.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing


class Context(typing.NamedTuple):
    args: typing.List[str] = []
    auto_cd: bool = False
    buffer_name: str = 'default'
    columns: str = ''
    cursor: int = 0
    direction: str = ''
    fnamewidth: int = 0
    listed: bool = False
    new: bool = False
    prev_bufnr: int = 0
    profile: bool = False
    resume: bool = False
    search: str = ''
    split: str = 'no'
    toggle: bool = False
    targets: typing.List[dict] = []
    winheight: int = 0
    winwidth: int = 0
