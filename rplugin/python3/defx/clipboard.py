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
                 candidates:
                 typing.List[typing.Dict[str, typing.Any]] = []) -> None:
        self.action = action
        self.candidates = candidates

    def _asdict(self) -> typing.Dict[str, typing.Any]:
        return {
            'action': str(self.action),
            'candidates': [{
                'word': x['word'],
                'is_directory': x['is_directory'],
                'is_opened_tree': x['is_opened_tree'],
                'level': x['level'],
                'action__path': str(x['action__path']),
            } for x in self.candidates]
        }
