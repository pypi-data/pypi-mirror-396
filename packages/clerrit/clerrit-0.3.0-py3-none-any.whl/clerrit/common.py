# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Philippe Proulx <eeppeliteloop@gmail.com>

import abc
import random
import re
import shlex
import string
import subprocess
import pathlib

import rich.console
import typer


class _AppError(RuntimeError):
    pass


def _print_error(msg: str):
    rich.console.Console(highlighter=None).print(f'[red][bold]✗ Error[/bold]: {msg}[/red]')


class _Cmd(abc.ABC):
    def __init__(self, change_number: int, remote: str, patchset: int | str | None,
                 claude_print: bool, claude_model: str | None, claude_permission_mode: str | None,
                 extra_prompt: str | None):
        self._console = rich.console.Console(highlighter=None)
        self._info('Initializing...')
        self._change_number = change_number
        self._remote = remote
        self._patchset: int | str | None = self._parse_patchset(patchset)
        self._claude_print = claude_print
        self._claude_model = claude_model
        self._claude_permission_mode = claude_permission_mode
        self._extra_prompt = extra_prompt

        if self._patchset is None:
            self._patchset = self._latest_patchset

        patchset_display = 'all patchsets' if self._patchset == 'all' else f'patchset [bold]{self._patchset}[/bold]'

        self._info(f'Remote [bold]{self._remote}[/bold], change [bold]{self._change_number}[/bold], and {patchset_display}')

    @staticmethod
    def _parse_patchset(patchset: int | str | None) -> int | str | None:
        if patchset is None or isinstance(patchset, int):
            return patchset

        if patchset == 'all':
            return 'all'

        try:
            return int(patchset)
        except ValueError:
            raise _AppError("Patchset must be an integer or 'all'")

    def _info(self, msg: str):
        self._console.print(f'[bold cyan]●[/bold cyan] {msg}')

    def _exec(self, cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        display_cmd = [
            (arg if len(arg) <= 64 else f'{arg[:64]}[bold]…[/bold]').replace('\n', ' ')
            for arg in cmd
        ]

        self._console.print(f'  [yellow][bold]‣ Running[/bold]: {shlex.join(display_cmd)}[/yellow]')

        try:
            return subprocess.run(cmd, **kwargs)
        except subprocess.CalledProcessError as exc:
            _print_error(f'Command failed with exit code {exc.returncode}: {shlex.join(cmd)}')

            if exc.stderr:
                _print_error(f'Standard error: {exc.stderr}')

            raise

    # Generates a random suffix for the branch name.
    @staticmethod
    def _generate_branch_suffix() -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    # Finds the Git root directory by walking up from the current
    # directory and returns it if found.
    @staticmethod
    def _find_git_root() -> pathlib.Path | None:
        path = pathlib.Path.cwd()

        while path != path.parent:
            if (path / '.git').exists():
                return path

            path = path.parent

    # Finds a `CONTRIBUTING*` file in the Git root directory and returns
    # its file name if found.
    @staticmethod
    def _find_contributing_file() -> pathlib.Path | None:
        git_root = _Cmd._find_git_root()

        if git_root is None:
            return

        m = list(git_root.glob('CONTRIBUTING*'))

        if m:
            return m[0]

    # Returns the latest patchset number from the remote.
    @property
    def _latest_patchset(self) -> int:
        refs = self._exec(['git', 'ls-remote', self._remote], check=True,
                          capture_output=True, text=True).stdout
        patchsets = [
            int(m.group(1)) for m in
            re.finditer(rf'refs/changes/\d{{2}}/{self._change_number}/(\d+)$',
                        refs, re.MULTILINE)
        ]

        if not patchsets:
            raise _AppError(f'No patchsets found for Gerrit change {self._change_number}')

        return max(patchsets)

    # Fetches the Gerrit patchset (or latest) from the remote.
    def _fetch_gerrit_change(self):
        self._info(f'Fetching Gerrit change [bold]{self._change_number}[/bold] from `[bold]{self._remote}[/bold]`...')

        # Gerrit refs format:
        #
        #     refs/changes/XX/CHANGE/PATCHSET
        #
        # where `XX` is the last two digits of the change number.
        last_two = f'{self._change_number % 100:02d}'

        # For `all` or `None`, fetch latest patchset
        if self._patchset is None or self._patchset == 'all':
            patchset = self._latest_patchset
        else:
            patchset = self._patchset

        ref = f'refs/changes/{last_two}/{self._change_number}/{patchset}'
        self._exec(['git', 'fetch', self._remote, ref], check=True)

    # Creates a new branch for the change.
    def _create_clerrit_branch(self):
        branch_name = f'clerrit-{self._change_number}-{self._generate_branch_suffix()}'
        self._info(f'Creating Git branch `[bold]{branch_name}[/bold]`...')
        self._exec(['git', 'checkout', '-b', branch_name, 'FETCH_HEAD'], check=True)
        self._info(f'Created Git branch `[bold]{branch_name}[/bold]`')

    @property
    @abc.abstractmethod
    def _prompt(self) -> str:
        ...

    # Runs Claude Code with the specific prompt + extra prompt.
    def _run_claude(self):
        cmd = ['claude']

        if self._claude_print:
            cmd.append('--print')

        if self._claude_model is not None:
            cmd += ['--model', self._claude_model]

        if self._claude_permission_mode is not None:
            cmd += ['--permission-mode', self._claude_permission_mode]

        prompt = self._prompt

        if self._extra_prompt:
            prompt += '\n\n' + self._extra_prompt

        cmd.append(prompt)
        self._exec(cmd, check=True)
