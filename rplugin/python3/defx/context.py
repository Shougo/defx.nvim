# ============================================================================
# FILE: context.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing


class Context(typing.NamedTuple):
    targets: typing.List[dict] = []
    args: typing.List[str] = []
    cursor: int = 0
