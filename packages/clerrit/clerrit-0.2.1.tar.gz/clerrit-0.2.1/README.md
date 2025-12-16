# clerrit

[![PyPI version](https://img.shields.io/pypi/v/clerrit)](https://pypi.org/project/clerrit/)

Supercharge your [Gerrit Code Review](https://www.gerritcodereview.com/)
workflow with LLM-powered code reviews and fixes!

__*clerrit*__ is a CLI tool which bridges Gerrit Code Review with
[Claude Code](https://claude.com/product/claude-code).

The current features are, for a given change and patchset:

* **Review a Gerrit change** using Claude
  Code, identifying bugs, security issues, edge cases, style problems,
  and missing error handling.

  This command only shows a code review report in Claude Code, helping
  you write your actual review comments on Gerrit. It doesn't send
  anything to Gerrit.

* **Address Gerrit code review comments** by having Claude Code fix the
  issues based on reviewer feedback.

  Claude Code fixes the code locally without running `git add`,
  `git commit`, or such. It doesn't send anything to Gerrit.

clerrit is meant to assist reviewers and developers,
not to replace them.

## Try it now!

* Make clerrit review the latest patchset of change&nbsp;27362 using the
  `review` remote of the current Git repository:

  ```
  $ uvx clerrit review 27362 --md
  ```

  You'll end up in Claude Code performing a code review, providing
  raw Markdown comments for specific files and line numbers.

* Make clerrit address the code review of the latest patchset of
  change&nbsp;1189 using the `review` remote of the current
  Git repository:

  ```
  $ uvx clerrit fix 1189
  ```

  You'll end up in Claude Code fixing the code to address the
  review comments.

See `clerrit --help` to learn more.

## What clerrit does

* `review` command:

  1. Fetches the patchset from the Gerrit remote.

  2. Creates a temporary local branch with the change.

  3. Launches Claude Code with a prompt to analyze the latest commit for
     bugs, security issues, edge cases, style problems, and missing error
     handling.

  4. If a `CONTRIBUTING*` file exists, mentions it as context.

* `fix` command:

  1. Fetches the patchset from the Gerrit remote.

  2. Creates a temporary local branch with the change.

  3. Queries the Gerrit server via SSH to retrieve all review comments
     for the patchset.

  4. Launches Claude Code with the comments and instructions to fix the
     reported issues (without staging, committing, or creating new files
     unless requested).

## Examples

* Review latest patchset of change 15753:

  ```
  $ clerrit review 15753
  ```

* Review patchset 3 of change 15753:

  ```
  $ clerrit review 15753 3
  ```

* Review with raw Markdown output for Gerrit comments:

  ```
  $ clerrit review 15753 --md
  ```

* Review using a custom remote instead of the default `review`:

  ```
  $ clerrit review 15753 --remote=gerrit
  ```

* Review with extra context for Claude:

  ```
  $ clerrit review 15753 --extra-prompt='Focus on memory safety.'
  ```

* Fix latest patchset based on review comments:

  ```
  $ clerrit fix 8472
  ```

* Fix a specific patchset:

  ```
  $ clerrit fix 8472 2
  ```

* Fix using a specific Claude model:

  ```
  $ clerrit fix 8472 --model=sonnet
  ```

* Fix in YOLO mode:

  ```
  $ clerrit fix 8472 --permission-mode=acceptEdits
  ```
