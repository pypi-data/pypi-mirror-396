# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Philippe Proulx <eeppeliteloop@gmail.com>

import clerrit.common


class _Cmd(clerrit.common._Cmd):
    def __init__(self, change: str, remote: str, patchset: int | None,
                 claude_print: bool, claude_model: str | None, claude_permission_mode: str | None,
                 extra_prompt: str | None, md: bool):
        super().__init__(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
                         extra_prompt)
        self._md = md
        self._run()

    def _run(self):
        self._fetch_gerrit_change()
        self._create_clerrit_branch()
        self._info('Starting review')
        self._run_claude()
        self._info('Done')

    @property
    def _prompt(self) -> str:
        contributing_file = self._find_contributing_file()
        contributing_line = f'Read `{contributing_file.name}` for project-specific guidelines.\n\n' if contributing_file else ''
        md_format = ', formatted as raw Markdown in a code block, without any "```markdown", ready to be copied as a Gerrit comment' if self._md else ''

        return f'''Review the last commit on the current branch. This is a Gerrit change awaiting review.

{contributing_line}Analyze the diff for:

- Bugs or logic errors.
- Security issues.
- Edge cases not handled.
- Style/readability issues.
- Missing error handling.

Only report genuine issues. Do NOT nitpick or invent problems where none exist.

Use this output format for your report: one or more blocks as follows, WITHOUT any general summary/conclusion:

1. A heading starting with `📄` followed with the file path and line number.
2. Your review comment here{md_format}.
3. Three empty lines.

If the change looks good, just say so briefly.
'''


# Runs the `review` command.
def _run(change: str, remote: str, patchset: int | None,
         claude_print: bool, claude_model: str | None, claude_permission_mode: str | None,
         extra_prompt: str | None, md: bool):
    _Cmd(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
         extra_prompt, md)
