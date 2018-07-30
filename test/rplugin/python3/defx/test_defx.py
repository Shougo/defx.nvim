import pytest

from defx.view import View
from neovim import Nvim
from unittest.mock import create_autospec
from unittest.mock import MagicMock


def test_do_action():
    vim = create_autospec(Nvim)
    vim.channel_id = 0
    vim.vars = {}
    vim.call.return_value = ''
    vim.current = MagicMock()

    defx = View(vim, [])
    defx.redraw()
    defx.do_action('open')
