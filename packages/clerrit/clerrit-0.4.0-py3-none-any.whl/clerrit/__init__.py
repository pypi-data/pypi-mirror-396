# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Philippe Proulx <eeppeliteloop@gmail.com>

from importlib.metadata import version
from typing import Annotated

import typer

import clerrit.common
import clerrit.fix
import clerrit.review


_app = typer.Typer()


def _version_callback(value: bool):
    if value:
        print(f'clerrit {version("clerrit")}')
        raise typer.Exit()


@_app.callback()
def _callback(version: Annotated[bool | None,
                                 typer.Option('--version', '-V',
                                              callback=_version_callback,
                                              is_eager=True,
                                              help='Show version and exit')] = None):
    pass

# Common argument/option types
_ChangeArg = Annotated[int, typer.Argument(metavar='CHANGE', help='Gerrit change number')]
_RemoteOpt = Annotated[str, typer.Option('--remote', '-r', metavar='REMOTE',
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
                            typer.Option('--extra-prompt', '-e', metavar='PROMPT',
                                         help='Extra prompt to append')]


def _validate_fix_patchset(patchset: str | None):
    if patchset is None or patchset == 'all':
        return

    try:
        int(patchset)
    except ValueError:
        raise typer.BadParameter('expecting an integer or `all`')


@_app.command(name='fix')
def _fix(change: _ChangeArg,
         patchset: Annotated[str | None, typer.Argument(metavar='PATCHSET',
                                                        help='Gerrit patchset number or `all`')] = None,
         remote: _RemoteOpt = 'review',
         claude_print: _ClaudePrintOpt = False, claude_model: _ClaudeModelOpt = None,
         claude_permission_mode: _ClaudePermissionModeOpt = None,
         extra_prompt: _ExtraPromptOpt = None,
         no_fetch: Annotated[bool,
                             typer.Option('--no-fetch',
                                          help="Don't fetch the change; work with current tree")] = False):
    _validate_fix_patchset(patchset)
    clerrit.fix._run(change, remote, patchset, claude_print, claude_model, claude_permission_mode,
                     extra_prompt, no_fetch)


@_app.command(name='review')
def _review(change: _ChangeArg,
            patchset: Annotated[int | None, typer.Argument(metavar='PATCHSET',
                                                           help='Gerrit patchset number')] = None,
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
