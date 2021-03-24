# ============================================================================
# FILE: rplugin.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pynvim import Nvim
import typing

from defx.clipboard import Clipboard
from defx.view import View

Candidate = typing.Dict[str, typing.Union[str, bool]]


def _candidate(candidate: typing.Dict[str, typing.Any]) -> Candidate:
    return {
        'word': candidate['word'],
        'is_directory': candidate['is_directory'],
        'is_opened_tree': candidate['is_opened_tree'],
        'is_selected': candidate['is_selected'],
        'level': candidate['level'],
        'action__path': str(candidate['action__path']),
    }


class Rplugin:

    def __init__(self, vim: Nvim) -> None:
        self._vim = vim
        self._views: typing.List[View] = []
        self._clipboard = Clipboard()

    def init_channel(self) -> None:
        self._vim.vars['defx#_channel_id'] = self._vim.channel_id

    def start(self, args: typing.List[typing.Any]) -> None:
        [paths, context] = args
        self.get_view(context).init_paths(paths, context, self._clipboard)

    def _current_views(self) -> typing.List[View]:
        return [x for x in self._views
                if x._bufnr == self._vim.current.buffer.number]

    def do_action(self, args: typing.List[typing.Any]) -> None:
        views = self._current_views()
        if not views:
            return
        view = views[0]

        prev_paths = [x._cwd for x in view._defxs]
        prev_candidates = view._candidates

        view.do_action(args[0], args[1], args[2])

        paths = [x._cwd for x in view._defxs]
        if paths == prev_paths and view._candidates != prev_candidates:
            self.redraw([x for x in self._views if x != view])

    def get_candidate(self) -> Candidate:
        cursor = self._vim.call('line', '.')
        for view in self._current_views():
            return _candidate(view.get_cursor_candidate(cursor))
        return {}

    def get_candidates(self) -> typing.List[Candidate]:
        for view in self._current_views():
            return [_candidate(x) for x in view._candidates]
        return []

    def get_selected_candidates(self) -> typing.List[Candidate]:
        cursor = self._vim.call('line', '.')
        for view in self._current_views():
            candidates = view.get_selected_candidates(cursor)
            return [_candidate(x) for x in candidates]
        return []

    def get_context(self) -> typing.Dict[str, typing.Any]:
        for view in self._current_views():
            return view._context._asdict()
        return {}

    def get_view(self, context: typing.Dict[str, typing.Any]) -> View:
        views = [x for x in self._views
                 if context['buffer_name'] == x._context.buffer_name]
        if not views or context['new']:
            view = View(self._vim, len(self._views))
            views = [view]
            self._views.append(view)
        return views[0]

    def redraw(self, views: typing.List[View]) -> None:
        call = self._vim.call
        for view in [x for x in views if call('bufwinnr', x._bufnr) > 0]:
            view.redraw(True)
