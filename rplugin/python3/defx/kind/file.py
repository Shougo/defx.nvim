# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
import importlib
import mimetypes
import shutil
import subprocess
import typing

from defx.action import ActionAttr
from defx.base.kind import action
from defx.kind.filelike import Kind as Base
from defx.clipboard import ClipboardAction
from defx.context import Context
from defx.defx import Defx
from defx.util import cd, confirm, error, Candidate
from defx.util import readable
from defx.view import View


class Kind(Base):

    def __init__(self, vim: Nvim) -> None:
        self.vim = vim
        self.name = 'file'

    def is_readable(self, path: Path) -> bool:
        return readable(path)

    def get_home(self) -> Path:
        return Path.home()

    def path_maker(self, path: str) -> Path:
        return Path(path)

    def rmtree(self, path: Path) -> None:
        shutil.rmtree(str(path))

    def get_buffer_name(self, path: str) -> str:
        return path

    def preview_file(self, view: View, defx: Defx, context: Context,
                     candidate: Candidate) -> None:
        filepath = str(candidate['action__path'])
        guess_type = mimetypes.guess_type(filepath)[0]
        if (guess_type and guess_type.startswith('image/') and
                shutil.which('ueberzug') and shutil.which('bash')):
            self._preview_image(view, defx, context, candidate)
            return

        super().preview_file(view, defx, context, candidate)

    def paste(self, view: View, src: Path, dest: Path,
              cwd: str) -> None:
        if view._clipboard.source_name != 'file':
            view._clipboard.paster(str(src), str(dest))
            view._vim.command('redraw')
            return

        action = view._clipboard.action
        if action == ClipboardAction.COPY:
            if src.is_dir():
                shutil.copytree(str(src), dest)
            else:
                shutil.copy2(str(src), dest)
        elif action == ClipboardAction.MOVE:
            shutil.move(str(src), cwd)

            # Check rename
            if not src.is_dir() and view._vim.call('bufexists', str(src)):
                view._vim.call('defx#util#buffer_rename',
                               view._vim.call('bufnr', str(src)), str(dest))
        elif action == ClipboardAction.LINK:
            # Create the symbolic link to dest
            dest.symlink_to(src, target_is_directory=src.is_dir())

    def check_output(self, view: View, cwd: str,
                     args: typing.List[str]) -> None:
        output = subprocess.check_output(args, cwd=cwd)
        if output:
            view.print_msg(output)

    @action(name='change_vim_cwd', attr=ActionAttr.NO_TAGETS)
    def _change_vim_cwd(self, view: View, defx: Defx,
                        context: Context) -> None:
        """
        Change the current working directory.
        """
        cd(view._vim, defx._cwd)

    @action(name='execute_system')
    def _execute_system(self, view: View, defx: Defx,
                        context: Context) -> None:
        """
        Execute the file by system associated command.
        """
        for target in context.targets:
            view._vim.call('defx#util#open', str(target['action__path']))

    @action(name='preview')
    def _preview(self, view: View, defx: Defx, context: Context) -> None:
        candidate = view.get_cursor_candidate(context.cursor)
        if not candidate or candidate['action__path'].is_dir():
            return

        filepath = str(candidate['action__path'])
        guess_type = mimetypes.guess_type(filepath)[0]
        if (guess_type and guess_type.startswith('image/') and
                shutil.which('ueberzug') and shutil.which('bash')):
            self._preview_image(view, defx, context, candidate)
            return

        self.preview_file(view, defx, context, candidate)

    def _preview_image(self, view: View, defx: Defx,
                       context: Context, candidate: Candidate) -> None:
        filepath = str(candidate['action__path'])

        if filepath == view._previewed_img:
            view._previewed_img = ''
            return

        preview_image_sh = Path(__file__).parent.parent.joinpath(
            'preview_image.sh')

        wincol = context.wincol + view._vim.call('winwidth', 0)
        if wincol + context.preview_width > view._vim.options['columns']:
            wincol -= 2 * context.preview_width
        args = ['bash', str(preview_image_sh), filepath,
                wincol, 1, context.preview_width]

        self.execute_job(view, args)
        view._previewed_img = filepath

    @action(name='remove_trash', attr=ActionAttr.REDRAW)
    def _remove_trash(self, view: View, defx: Defx, context: Context) -> None:
        """
        Delete the file or directory.
        """
        if not context.targets:
            return

        if not importlib.util.find_spec('send2trash'):
            error(view._vim, '"Send2Trash" is not installed')
            return

        force = context.args[0] == 'force' if context.args else False
        if not force:
            message = 'Are you sure you want to delete {}?'.format(
                str(context.targets[0]['action__path'])
                if len(context.targets) == 1
                else str(len(context.targets)) + ' files')
            if not confirm(view._vim, message):
                return

        import send2trash
        for target in context.targets:
            target_path = str(target['action__path'])
            send2trash.send2trash(target_path)

            if view._vim.call('bufexists', target_path):
                view._vim.call('defx#util#buffer_delete',
                               view._vim.call('bufnr', target_path))
