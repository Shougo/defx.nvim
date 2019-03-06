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
    listed: bool = False
    new: bool = False
    prev_bufnr: int = 0
    prev_winid: int = 0
    profile: bool = False
    resume: bool = False
    root_marker: str = ''
    search: str = ''
    sort: str = ''
    show_ignored_files: bool = False
    split: str = 'no'
    toggle: bool = False
    targets: typing.List[typing.Dict[str, typing.Any]] = []
    wincol: int = 0
    winheight: int = 0
    winrow: int = 0
    winwidth: int = 0
