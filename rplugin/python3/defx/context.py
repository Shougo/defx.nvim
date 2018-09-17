# ============================================================================
# FILE: context.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing


class Context(typing.NamedTuple):
    args: typing.List[str] = []
    auto_cd: bool = False
    columns: str = ''
    cursor: int = 0
    fnamewidth: int = 0
    search: str = ''
    split: str = 'no'
    targets: typing.List[dict] = []
