# ============================================================================
# FILE: base.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from abc import abstractmethod


class Base(object):

    def __init__(self, vim):
        self.vim = vim
        self.name = 'base'

    @abstractmethod
    def gather_candidate(self, context):
        pass
