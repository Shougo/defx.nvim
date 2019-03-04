# ============================================================================
# FILE: __init__.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from enum import auto, IntFlag
import typing

from defx.context import Context
from defx.defx import Defx
from defx.view import View


class ActionAttr(IntFlag):
    REDRAW = auto()
    MARK = auto()
    NO_TAGETS = auto()
    TREE = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


def do_action(view: View, defx: Defx,
              action_name: str, context: Context) -> bool:
    """
    Do "action_name" action.
    """
    actions: typing.Dict[str, ActionTable] = defx._source.kind.get_actions()

    if action_name not in actions:
        return True

    action = actions[action_name]

    if ActionAttr.NO_TAGETS not in action.attr and view._selected_candidates:
        # Clear marks
        view._selected_candidates = []
        view.redraw()

    action.func(view, defx, context)

    if action_name != 'repeat':
        view._prev_action = action_name

    if ActionAttr.MARK in action.attr:
        # Update marks
        view.redraw()
    elif ActionAttr.TREE in action.attr:
        # Update opened state
        view._opened_candidates = [
            x[0] for x in enumerate(view._candidates) if x[1]['is_opened']]
        view.redraw()
    elif ActionAttr.REDRAW in action.attr:
        # Redraw
        view.redraw(True)
    return False
