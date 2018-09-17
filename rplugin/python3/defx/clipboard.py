# ============================================================================
# FILE: clipboard.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, Enum
import typing


class ClipboardAction(Enum):
    MOVE = auto()
    COPY = auto()


class Clipboard():
    def __init__(self,
                 action: ClipboardAction = ClipboardAction.COPY,
                 candidates: typing.List[dict] = []) -> None:
        self.action = action
        self.candidates = candidates
