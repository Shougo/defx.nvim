# ============================================================================
# FILE: kind.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
import json
import re
import inspect
import typing
from functools import wraps, partial

from defx.action import ActionAttr
from defx.action import ActionTable
from defx.action import do_action
from defx.context import Context
from defx.defx import Defx
from defx.session import Session
from defx.view import View

Kind = typing.Any
ACTION_FUNC = typing.Callable[[Kind, View, Defx, Context], None]


class ActionFunc:
    def __init__(self, name: str, attr: ActionAttr, func: ACTION_FUNC):
        self._is_action = True
        self._name = name
        self._attr = attr
        self._func = func

    def __call__(self, kind: Kind, view: View, defx: Defx,
                 context: Context) -> None:
        return self._func(kind, view, defx, context)


def action(name: str, attr: ActionAttr = ActionAttr.NONE
           ) -> typing.Callable[[ACTION_FUNC], ACTION_FUNC]:
    def wrapper(func: ACTION_FUNC) -> ACTION_FUNC:
        f = ActionFunc(name, attr, func)

        @wraps(f)
        def inner_wrapper(kind: Kind, view: View, defx: Defx,
                          context: Context) -> None:
            return f(kind, view, defx, context)
        return inner_wrapper
    return wrapper


class Base:

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'base'

    def get_actions(self) -> typing.Dict[str, ActionTable]:
        def predicate(o: object) -> bool:
            return hasattr(o, '_is_action')
        actions = {}
        for member in inspect.getmembers(self, predicate):
            func = member[1]
            actions[func._name] = ActionTable(
                func=partial(func._func, self), attr=func._attr)
        return actions

    @action(name='add_session', attr=ActionAttr.NO_TAGETS)
    def _add_session(self, view: View, defx: Defx, context: Context) -> None:
        path = context.args[0] if context.args else defx._cwd
        if path[-1] == '/':
            # Remove the last slash
            path = path[: -1]

        opened_candidates = [] if context.args else list(
            defx._opened_candidates)
        opened_candidates.sort()

        session: Session
        if path in view._sessions:
            old_session = view._sessions[path]
            session = Session(
                name=old_session.name, path=old_session.path,
                opened_candidates=opened_candidates)
        else:
            name = Path(path).name
            session = Session(
                name=name, path=path,
                opened_candidates=opened_candidates)
            view.print_msg(f'session "{name}" is created')

        view._sessions[session.path] = session

        self._save_session(view, defx, context)

    @action(name='call', attr=ActionAttr.REDRAW)
    def _call(self, view: View, defx: Defx, context: Context) -> None:
        """
        Call the function.
        """
        function = context.args[0] if context.args else None
        if not function:
            return

        dict_context = context._asdict()
        dict_context['cwd'] = defx._cwd
        dict_context['targets'] = [
            str(x['action__path']) for x in context.targets]
        view._vim.call(function, dict_context)

    @action(name='change_filtered_files', attr=ActionAttr.REDRAW)
    def _change_filtered_files(self, view: View, defx: Defx,
                               context: Context) -> None:
        filtered_files = context.args[0] if context.args else view._vim.call(
            'defx#util#input',
            f'{".".join(defx._filtered_files)} -> ',
            '.'.join(defx._filtered_files))
        defx._filtered_files = filtered_files.split(',')

    @action(name='change_ignored_files', attr=ActionAttr.REDRAW)
    def _change_ignored_files(self, view: View, defx: Defx,
                              context: Context) -> None:
        ignored_files = context.args[0] if context.args else view._vim.call(
            'defx#util#input',
            f'{".".join(defx._ignored_files)} -> ',
            '.'.join(defx._ignored_files))
        defx._ignored_files = ignored_files.split(',')

    @action(name='clear_select_all',
            attr=ActionAttr.MARK | ActionAttr.NO_TAGETS)
    def _clear_select_all(self, view: View, defx: Defx,
                          context: Context) -> None:
        for candidate in [x for x in view._candidates
                          if x['_defx_index'] == defx._index]:
            candidate['is_selected'] = False

    @action(name='close_tree', attr=ActionAttr.TREE | ActionAttr.CURSOR_TARGET)
    def _close_tree(self, view: View, defx: Defx, context: Context) -> None:
        for target in context.targets:
            if target['is_directory'] and target['is_opened_tree']:
                view.close_tree(target['action__path'], defx._index)
            else:
                view.close_tree(target['action__path'].parent, defx._index)
                view.search_file(target['action__path'].parent, defx._index)

    @action(name='delete_session', attr=ActionAttr.NO_TAGETS)
    def _delete_session(self, view: View, defx: Defx,
                        context: Context) -> None:
        if not context.args:
            return

        session_name = context.args[0]
        if session_name not in view._sessions:
            return
        view._sessions.pop(session_name)

        self._save_session(view, defx, context)

    @action(name='load_session', attr=ActionAttr.NO_TAGETS)
    def _load_session(self, view: View, defx: Defx, context: Context) -> None:
        session_file = Path(context.session_file)
        if not context.session_file or not session_file.exists():
            return

        loaded_session = json.loads(session_file.read_text())
        if 'sessions' not in loaded_session:
            return

        view._sessions = {}
        for path, session in loaded_session['sessions'].items():
            view._sessions[path] = Session(**session)

        view._vim.current.buffer.vars['defx#_sessions'] = [
            x._asdict() for x in view._sessions.values()
        ]

    @action(name='multi')
    def _multi(self, view: View, defx: Defx, context: Context) -> None:
        for arg in context.args:
            args: typing.List[str]
            if isinstance(arg, list):
                args = arg
            else:
                args = [arg]
            do_action(view, defx, args[0], context._replace(args=args[1:]))

    @action(name='check_redraw', attr=ActionAttr.NO_TAGETS)
    def _nop(self, view: View, defx: Defx, context: Context) -> None:
        pass

    @action(name='open_tree', attr=ActionAttr.TREE | ActionAttr.CURSOR_TARGET)
    def _open_tree(self, view: View, defx: Defx, context: Context) -> None:
        nested = False
        recursive_level = 0
        toggle = False
        for arg in context.args:
            if arg == 'nested':
                nested = True
            elif arg == 'recursive':
                recursive_level = 20
            elif re.search(r'recursive:\d+', arg):
                recursive_level = int(arg.split(':')[1])
            elif arg == 'toggle':
                toggle = True

        for target in [x for x in context.targets if x['is_directory']]:
            if toggle and target['is_directory'] and target['is_opened_tree']:
                self._close_tree(
                    view, defx, context._replace(targets=[target]))
            else:
                view.open_tree(target['action__path'],
                               defx._index, nested, recursive_level)

    @action(name='open_tree_recursive',
            attr=ActionAttr.TREE | ActionAttr.CURSOR_TARGET)
    def _open_tree_recursive(self, view: View, defx: Defx,
                             context: Context) -> None:
        level = context.args[0] if context.args else '20'
        self._open_tree(view, defx, context._replace(
            args=context.args + ['recursive:' + level]))

    @action(name='open_or_close_tree',
            attr=ActionAttr.TREE | ActionAttr.CURSOR_TARGET)
    def _open_or_close_tree(self, view: View, defx: Defx,
                            context: Context) -> None:
        self._open_tree(view, defx, context._replace(
            args=context.args + ['toggle']))

    @action(name='print')
    def _print(self, view: View, defx: Defx, context: Context) -> None:
        for target in context.targets:
            view.print_msg(str(target['action__path']))

    @action(name='quit', attr=ActionAttr.NO_TAGETS)
    def _quit(self, view: View, defx: Defx, context: Context) -> None:
        view.quit()

    @action(name='redraw', attr=ActionAttr.NO_TAGETS)
    def _redraw(self, view: View, defx: Defx, context: Context) -> None:
        view.redraw(True)

    @action(name='repeat', attr=ActionAttr.MARK)
    def _repeat(self, view: View, defx: Defx, context: Context) -> None:
        do_action(view, defx, view._prev_action, context)

    @action(name='resize', attr=ActionAttr.NO_TAGETS)
    def _resize(self, view: View, defx: Defx, context: Context) -> None:
        if not context.args:
            return

        view._context = view._context._replace(winwidth=int(context.args[0]))
        view._init_window()
        view.redraw(True)

    @action(name='save_session', attr=ActionAttr.NO_TAGETS)
    def _save_session(self, view: View, defx: Defx, context: Context) -> None:
        view._vim.current.buffer.vars['defx#_sessions'] = [
            x._asdict() for x in view._sessions.values()
        ]

        if not context.session_file:
            return

        session_file = Path(context.session_file)
        session_file.write_text(json.dumps({
            'version': view._session_version,
            'sessions': {x: y._asdict() for x, y in view._sessions.items()}
        }))

    @action(name='search', attr=ActionAttr.NO_TAGETS)
    def _search(self, view: View, defx: Defx, context: Context) -> None:
        if not context.args or not context.args[0]:
            return

        search_path = context.args[0]
        view.search_recursive(Path(search_path), defx._index)

    @action(name='toggle_columns', attr=ActionAttr.REDRAW)
    def _toggle_columns(self, view: View, defx: Defx,
                        context: Context) -> None:
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
        view._init_columns(columns)

    @action(name='toggle_ignored_files', attr=ActionAttr.REDRAW)
    def _toggle_ignored_files(self, view: View, defx: Defx,
                              context: Context) -> None:
        defx._enabled_ignored_files = not defx._enabled_ignored_files

    @action(name='toggle_select', attr=ActionAttr.MARK | ActionAttr.NO_TAGETS)
    def _toggle_select(self, view: View, defx: Defx, context: Context) -> None:
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate:
            return

        candidate['is_selected'] = not candidate['is_selected']

    @action(name='toggle_select_all',
            attr=ActionAttr.MARK | ActionAttr.NO_TAGETS)
    def _toggle_select_all(self, view: View, defx: Defx,
                           context: Context) -> None:
        for candidate in [x for x in view._candidates
                          if not x['is_root'] and
                          x['_defx_index'] == defx._index]:
            candidate['is_selected'] = not candidate['is_selected']

    @action(name='toggle_select_visual',
            attr=ActionAttr.MARK | ActionAttr.NO_TAGETS)
    def _toggle_select_visual(self, view: View, defx: Defx,
                              context: Context) -> None:
        if context.visual_start <= 0 or context.visual_end <= 0:
            return

        start = context.visual_start - 1
        end = min([context.visual_end, len(view._candidates)])
        for candidate in [x for x in view._candidates[start:end]
                          if not x['is_root'] and
                          x['_defx_index'] == defx._index]:
            candidate['is_selected'] = not candidate['is_selected']

    @action(name='toggle_sort', attr=ActionAttr.MARK |
            ActionAttr.NO_TAGETS | ActionAttr.REDRAW)
    def _toggle_sort(self, view: View, defx: Defx, context: Context) -> None:
        """
        Toggle the current sort method.
        """
        sort = context.args[0] if context.args else ''
        if sort == defx._sort_method:
            # Use default sort method
            defx._sort_method = context.sort
        else:
            defx._sort_method = sort

    @action(name='yank_path')
    def _yank_path(self, view: View, defx: Defx, context: Context) -> None:
        mods = context.args[0] if context.args else ''
        paths = [str(x['action__path']) for x in context.targets]
        if mods:
            paths = [view._vim.call('fnamemodify', x, mods) for x in paths]
        yank = '\n'.join(paths)
        view._vim.call('setreg', '"', yank)
        if (view._vim.call('has', 'clipboard') or
                view._vim.call('has', 'xterm_clipboard')):
            view._vim.call('setreg', '+', yank)
        view.print_msg('Yanked:\n' + yank)
