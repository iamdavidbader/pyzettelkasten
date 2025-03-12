import subprocess
import click

import subprocess

def fzf_select(items):
    """Pipes a list of items to fzf with bat preview, VS Code shortcut, and Vim-style navigation."""
    if not items:
        click.echo("No results found.")
        return None

    try:
        result = subprocess.run(
            [
                "fzf",
                "--preview", "bat --color=always --style=plain --line-range=:100 {}",
                "--bind", "ctrl-o:execute(code {})+abort",  # Open file in VS Code
                "--bind", "ctrl-j:down,ctrl-k:up",  # Enable Vim-style navigation
                "--bind", "ctrl-y:execute-silent(echo {} | clip)+abort"  # Copy filename to clipboard
            ],
            input="\n".join(items),
            text=True,
            capture_output=True
        )

        return result.stdout.strip() or None

    except FileNotFoundError:
        click.echo("Error: 'fzf' or 'bat' is not installed or not in PATH.", err=True)
        return None