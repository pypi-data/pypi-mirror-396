# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Philippe Proulx <eeppeliteloop@gmail.com>

from typing import Annotated

import typer

import clerrit.common
import clerrit.fix
import clerrit.review


_app = typer.Typer()

# Common argument/option types
_ChangeArg = Annotated[str, typer.Argument(metavar='CHANGE')]
_PatchsetArg = Annotated[int | None, typer.Argument(metavar='PATCHSET')]
_RemoteOpt = Annotated[str, typer.Option('--remote', '-r',
                                         help='Use the Gerrit remote REMOTE')]
_ClaudePrintOpt = Annotated[bool,
                            typer.Option('--print', '-p',
                                         help='Print response and exit (`claude --print`)')]
_ClaudeModelOpt = Annotated[str | None,
                            typer.Option('--model', '-m', metavar='MODEL',
                                         help='Model to use (`claude --model=MODEL`)')]
_ClaudePermissionModeOpt = Annotated[str | None,
                                     typer.Option('--permission-mode', metavar='MODE',
                                                  help='Permission mode (`claude --permission-mode=MODE`)')]
_ExtraPromptOpt = Annotated[str | None,
                            typer.Option('--extra-prompt', '-e',
                                         help='Extra prompt to append')]


@_app.command(name='fix')
def _fix(change: _ChangeArg, patchset: _PatchsetArg = None, remote: _RemoteOpt = 'review',
         claude_print: _ClaudePrintOpt = False, claude_model: _ClaudeModelOpt = None,
         claude_permission_mode: _ClaudePermissionModeOpt = None,
         extra_prompt: _ExtraPromptOpt = None):
    clerrit.fix._run(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
                     extra_prompt)


@_app.command(name='review')
def _review(change: _ChangeArg, patchset: _PatchsetArg = None,
            remote: _RemoteOpt = 'review', claude_print: _ClaudePrintOpt = False,
            claude_model: _ClaudeModelOpt = None,
            claude_permission_mode: _ClaudePermissionModeOpt = None,
            extra_prompt: _ExtraPromptOpt = None,
            md: Annotated[bool,
                          typer.Option('--md',
                                       help='Output comments as pure Markdown for Gerrit')] = False):
    clerrit.review._run(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
                        extra_prompt, md)


def _main():
    try:
        _app()
    except clerrit.common._AppError as exc:
        clerrit.common._print_error(str(exc))
        raise SystemExit(1)
