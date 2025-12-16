# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Philippe Proulx <eeppeliteloop@gmail.com>

import dataclasses
import json
import pathlib
import re
import tempfile

import clerrit.common


@dataclasses.dataclass(frozen=True)
class _SshInfo:
    user: str | None
    host: str
    port: int

    @property
    def dst(self) -> str:
        if self.user:
            return f'{self.user}@{self.host}'

        return self.host


class _Cmd(clerrit.common._Cmd):
    def __init__(self, change: str, remote: str, patchset: int | None,
                 claude_print: bool, claude_model: str | None, claude_permission_mode: str | None,
                 extra_prompt: str | None):
        super().__init__(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
                         extra_prompt)
        self._run()

    def _run(self):
        self._fetch_gerrit_change()
        self._create_clerrit_branch()
        self._info('Downloading Gerrit comments...')
        self._comments_path = self._fetch_gerrit_comments()
        self._info(f'Created `[bold]{self._comments_path}[/bold]`')
        self._info('Starting fix')
        self._run_claude()
        self._info('Done')


    @property
    def _gerrit_ssh_info(self) -> _SshInfo:
        url = self._exec(['git', 'remote', 'get-url', self._remote], check=True,
                         capture_output=True, text=True).stdout.strip()

        # Try `ssh://` URL format
        m = re.match(r'ssh://(?:([^@]+)@)?([^:/]+)(?::(\d+))?/', url)

        if m:
            port = int(m.group(3)) if m.group(3) else 29418
            return _SshInfo(m.group(1), m.group(2), port)

        # Try SCP-style format
        m = re.match(r'(?:([^@]+)@)?([^:]+):', url)

        if m:
            return _SshInfo(m.group(1), m.group(2), 29418)

        raise clerrit.common._AppError(f'Cannot parse SSH URL `{url}` from remote `{self._remote}`')

    @property
    def _target_patchset(self) -> int:
        if self._patchset is not None:
            return self._patchset

        return self._latest_patchset

    # Fetches Gerrit review comments and writes them to a temporary
    # Markdown file, returning its path.
    def _fetch_gerrit_comments(self) -> pathlib.Path:
        ssh_info = self._gerrit_ssh_info

        # Build SSH command
        ssh_cmd = [
            'ssh', '-p', str(ssh_info.port), ssh_info.dst,
            'gerrit', 'query', '--comments', '--patch-sets', '--format=JSON',
            f'change:{self._change_number}',
        ]

        output = self._exec(ssh_cmd, check=True, capture_output=True, text=True).stdout

        # Parse line-delimited JSON
        change_data = None

        for line in output.strip().split('\n'):
            obj = json.loads(line)

            # Skip stats object
            if obj.get('type') == 'stats':
                continue

            change_data = obj
            break

        if change_data is None:
            raise clerrit.common._AppError(f'No change data found for change {self._change_number}')

        md = self._gerrit_comments_to_md(change_data)

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', prefix='clerrit-', suffix='.md',
                                         delete=False) as f:
            f.write(md)
            return pathlib.Path(f.name)

    # Converts the Gerrit change data `change_data` to a Markdown
    # document containing a summary and individual review comments.
    def _gerrit_comments_to_md(self, change_data: dict) -> str:
        # Get change info
        subject = change_data.get('subject', 'Unknown')
        project = change_data.get('project', 'Unknown')
        branch = change_data.get('branch', 'Unknown')
        owner = change_data.get('owner', {}).get('name', 'Unknown')

        # Get comments from target patchset
        filtered_comments = []

        for ps in change_data.get('patchSets', []):
            if ps.get('number') == self._target_patchset:
                filtered_comments = ps.get('comments', [])
                break

        # Build Markdown
        lines = [
            '# Code review',
            '',
            f'- **Subject**: {subject}',
            f'- **Change**: {self._change_number}',
            f'- **Patchset**: {self._target_patchset}',
            f'- **Project**: {project}',
            f'- **Branch**: {branch}',
            f'- **Owner**: {owner}',
            '',
            'Review comments follow.',
            '',
        ]

        if not filtered_comments:
            raise clerrit.common._AppError(f'No review comments for patchset {self._patchset} of change {self._change_number}')

        for comment in filtered_comments:
            file_path = comment.get('file', 'Unknown')
            line_num = comment.get('line', '?')
            message = comment.get('message', '').strip()

            # Skip trivial responses
            if re.fullmatch(r'(?:|ok|okay|done|ack(?:nowledged)?)\.?', message.lower()):
                continue

            if message:
                lines += [
                    f'## {file_path}:{line_num}',
                    '',
                    message,
                    '',
                ]

        return '\n'.join(lines)

    @property
    def _prompt(self) -> str:
        return f'''Address the code review comments in `{self._comments_path}`.

Rules:

- Work on the current branch which contains the code to fix.
- Do NOT use `git` (no staging, no committing, no branch operations).
- Only modify existing files to address the review comments.
- Do NOT add new files unless explicitly requested in a comment.
'''


# Runs the `fix` command.
def _run(change: str, remote: str, patchset: int | None,
         claude_print: bool, claude_model: str | None, claude_permission_mode: str | None,
         extra_prompt: str | None):
    _Cmd(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
         extra_prompt)
