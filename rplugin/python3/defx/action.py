# ============================================================================
# FILE: action.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import copy
from enum import auto, IntFlag
import typing

from defx.context import Context
from defx.defx import Defx
from defx.view import View


class ActionAttr(IntFlag):
    REDRAW = auto()
    MARK = auto()
    NONE = 0


class ActionTable(typing.NamedTuple):
    func: typing.Callable[[View, Defx, Context], None]
    attr: ActionAttr = ActionAttr.NONE


def do_action(view: View, defx: Defx,
              action_name: str, context: Context) -> bool:
    """
    Do "action_name" action.
    """
    actions: typing.Dict[str, ActionTable] = copy.copy(defx._source.actions)
    actions.update(DEFAULT_ACTIONS)

    if action_name not in actions:
        return True

    action = actions[action_name]

    if ActionAttr.MARK not in action.attr and view._selected_candidates:
        # Clear marks
        view._selected_candidates = []
        view.redraw()

    action.func(view, defx, context)

    if action_name != 'repeat':
        view._prev_action = action_name

    if ActionAttr.MARK in action.attr:
        # Update marks
        view.redraw()
    elif ActionAttr.REDRAW in action.attr:
        # Redraw
        view.redraw(True)
    return False


def _call(view: View, defx: Defx, context: Context) -> None:
    """
    Call the function.
    """
    function = context.args[0] if context.args else None
    if not function:
        return

    dict_context = context._asdict()
    dict_context['targets'] = [
        str(x['action__path']) for x in context.targets]
    view._vim.call(function, dict_context)


def _multi(view: View, defx: Defx, context: Context) -> None:
    for arg in context.args:
        args: typing.List[str]
        if isinstance(arg, list):
            args = arg
        else:
            args = [arg]
        do_action(view, defx, args[0], context._replace(args=args[1:]))


def _print(view: View, defx: Defx, context: Context) -> None:
    for target in context.targets:
        view.print_msg(str(target['action__path']))


def _quit(view: View, defx: Defx, context: Context) -> None:
    view.quit()


def _redraw(view: View, defx: Defx, context: Context) -> None:
    view.redraw(True)
    if context.args and context.args[0]:
        view.search_tree(context.args[0], defx._index)


def _repeat(view: View, defx: Defx, context: Context) -> None:
    do_action(view, defx, view._prev_action, context)


def _toggle_columns(view: View, defx: Defx, context: Context) -> None:
    """
    Toggle the current columns.
    """
    columns = (context.args[0] if context.args else '').split(':')
    if not columns:
        return
    current_columns = [x.name for x in view._columns]
    if columns == current_columns:
        # Use default columns
        columns = context.columns.split(':')
    view.init_columns(columns)


def _toggle_ignored_files(view: View, defx: Defx, context: Context) -> None:
    defx._enabled_ignored_files = not defx._enabled_ignored_files


def _toggle_select(view: View, defx: Defx, context: Context) -> None:
    index = context.cursor - 1
    if index in view._selected_candidates:
        view._selected_candidates.remove(index)
    else:
        view._selected_candidates.append(index)


def _toggle_select_all(view: View, defx: Defx, context: Context) -> None:
    for [index, candidate] in enumerate(view._candidates):
        if (not candidate.get('is_root', False) and
                candidate['_defx_index'] == defx._index):
            if index in view._selected_candidates:
                view._selected_candidates.remove(index)
            else:
                view._selected_candidates.append(index)


def _toggle_sort(view: View, defx: Defx, context: Context) -> None:
    """
    Toggle the current sort method.
    """
    sort = context.args[0] if context.args else ''
    if sort == defx._sort_method:
        # Use default sort method
        defx._sort_method = context.sort
    else:
        defx._sort_method = sort


def _yank_path(view: View, defx: Defx, context: Context) -> None:
    yank = '\n'.join([str(x['action__path']) for x in context.targets])
    view._vim.call('setreg', '"', yank)
    if (view._vim.call('has', 'clipboard') or
            view._vim.call('has', 'xterm_clipboard')):
        view._vim.call('setreg', '+', yank)
    view.print_msg('Yanked:\n' + yank)


DEFAULT_ACTIONS = {
    'call': ActionTable(func=_call, attr=ActionAttr.REDRAW),
    'multi': ActionTable(func=_multi),
    'print': ActionTable(func=_print),
    'quit': ActionTable(func=_quit),
    'redraw': ActionTable(func=_redraw),
    'repeat': ActionTable(func=_repeat, attr=ActionAttr.MARK),
    'toggle_columns': ActionTable(
        func=_toggle_columns, attr=ActionAttr.REDRAW),
    'toggle_ignored_files': ActionTable(
        func=_toggle_ignored_files, attr=ActionAttr.REDRAW),
    'toggle_select': ActionTable(
        func=_toggle_select, attr=ActionAttr.MARK),
    'toggle_select_all': ActionTable(
        func=_toggle_select_all, attr=ActionAttr.MARK),
    'toggle_sort': ActionTable(
        func=_toggle_sort, attr=ActionAttr.REDRAW),
    'yank_path': ActionTable(func=_yank_path),
}
