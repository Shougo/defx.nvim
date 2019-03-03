# ============================================================================
# FILE: kind.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import typing

from defx.action import ActionAttr
from defx.action import ActionTable
from defx.action import do_action
from defx.context import Context
from defx.defx import Defx
from defx.view import View
from defx.util import Nvim


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'

    def get_actions(self) -> typing.Dict[str, ActionTable]:
        return {
            'call': ActionTable(
                func=_call, attr=ActionAttr.REDRAW),
            'close_tree': ActionTable(
                func=_close_tree, attr=ActionAttr.REDRAW),
            'multi': ActionTable(func=_multi),
            'open_tree': ActionTable(
                func=_open_tree, attr=ActionAttr.REDRAW),
            'open_or_close_tree': ActionTable(
                func=_open_or_close_tree, attr=ActionAttr.REDRAW),
            'print': ActionTable(func=_print),
            'quit': ActionTable(
                func=_quit, attr=ActionAttr.NO_TARGET),
            'redraw': ActionTable(
                func=_redraw, attr=ActionAttr.NO_TARGET),
            'repeat': ActionTable(
                func=_repeat, attr=ActionAttr.MARK),
            'search': ActionTable(
                func=_search, attr=ActionAttr.NO_TARGET),
            'toggle_columns': ActionTable(
                func=_toggle_columns, attr=ActionAttr.REDRAW),
            'toggle_ignored_files': ActionTable(
                func=_toggle_ignored_files, attr=ActionAttr.REDRAW),
            'toggle_select': ActionTable(
                func=_toggle_select,
                attr=ActionAttr.MARK | ActionAttr.NO_TARGET),
            'toggle_select_all': ActionTable(
                func=_toggle_select_all,
                attr=ActionAttr.MARK | ActionAttr.NO_TARGET),
            'toggle_sort': ActionTable(
                func=_toggle_sort,
                attr=ActionAttr.MARK | ActionAttr.NO_TARGET),
            'yank_path': ActionTable(func=_yank_path),
        }


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


def _close_tree(view: View, defx: Defx, context: Context) -> None:
    pass


def _multi(view: View, defx: Defx, context: Context) -> None:
    for arg in context.args:
        args: typing.List[str]
        if isinstance(arg, list):
            args = arg
        else:
            args = [arg]
        do_action(view, defx, args[0], context._replace(args=args[1:]))


def _open_tree(view: View, defx: Defx, context: Context) -> None:
    pass


def _open_or_close_tree(view: View, defx: Defx, context: Context) -> None:
    pass


def _print(view: View, defx: Defx, context: Context) -> None:
    for target in context.targets:
        view.print_msg(str(target['action__path']))


def _quit(view: View, defx: Defx, context: Context) -> None:
    view.quit()


def _redraw(view: View, defx: Defx, context: Context) -> None:
    view.redraw(True)


def _repeat(view: View, defx: Defx, context: Context) -> None:
    do_action(view, defx, view._prev_action, context)


def _search(view: View, defx: Defx, context: Context) -> None:
    if context.args and context.args[0]:
        view.search_tree(context.args[0], defx._index)


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
