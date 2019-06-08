# ============================================================================
# FILE: defx/session.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import json
import typing

from defx.session import Session
from defx.util import Nvim
from denite.kind.command import Kind as Command
from denite.source.base import Base
from pathlib import Path


class Source(Base):

    def __init__(self, vim: Nvim):
        super().__init__(vim)

        self.name = 'defx/session'
        self.kind = Kind(vim)
        self._sessions: typing.Dict[str, Session] = {}

    def on_init(self, context: dict):
        self._sessions = {}

        options = self.vim.current.buffer.options
        bufvars = self.vim.current.buffer.vars
        if 'defx' not in bufvars or options['filetype'] != 'defx':
            return

        session_file = bufvars['defx']['context']['session_file']
        session_path = Path(session_file)
        if not session_file or not session_path.exists():
            return

        loaded_session = json.loads(session_path.read_text())
        if 'sessions' not in loaded_session:
            return

        for path, session in loaded_session['sessions'].items():
            self._sessions[path] = Session(**session)

    def gather_candidates(self, context: dict):
        max_name = max([self.vim.call('strwidth', x.name)
                        for x in self._sessions.values()])
        word_format = '{0:<' + str(max_name) + '} - {1}'
        return [{
            'word': word_format.format(x.name, x.path),
            'action__command': f"call defx#call_action('cd', ['{x.path}'])",
            'source__path': x.path,
        } for x in self._sessions.values()]


class Kind(Command):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'defx/session'

    def action_delete(self, context):
        for candidate in context['targets']:
            self.vim.call('defx#call_action', 'delete_session',
                          candidate['source__path'])
