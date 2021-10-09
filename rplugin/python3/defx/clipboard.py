# ============================================================================
# FILE: clipboard.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, Enum
import typing


class ClipboardAction(Enum):
    NONE = auto()
    MOVE = auto()
    COPY = auto()
    LINK = auto()


def default_paster(src: str, dest: str) -> None:
    pass


class Clipboard():
    def __init__(self,
                 action: ClipboardAction = ClipboardAction.NONE,
                 candidates:
                 typing.List[typing.Dict[str, typing.Any]] = [],
                 source_name: str = '',
                 mode: str = '',
                 paster: typing.Callable[[str, str], None] = default_paster
                 ) -> None:
        self.action = action
        self.candidates = candidates
        self.source_name = source_name
        self.mode = mode
        self.paster = paster
