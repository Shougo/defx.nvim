# ============================================================================
# FILE: indent.py
# AUTHOR: GuoPan Zhao <zgpio@qq.com>
# License: MIT license
# ============================================================================

from defx.base.column import Base
from defx.context import Context
from defx.util import Nvim

import typing


class Column(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.name = 'indent'
        self._current_len = 0

    def get(self, context: Context,
            candidate: typing.Dict[str, typing.Any]) -> str:
        indent = ' ' * candidate['level']
        self._current_len = len(indent)
        return indent

    def length(self, context: Context) -> int:
        return typing.cast(int, self._current_len)
