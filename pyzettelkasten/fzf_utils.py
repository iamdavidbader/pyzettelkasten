import subprocess
import click

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
                "--bind", "ctrl-o:execute(code {})+abort",
                "--bind", "ctrl-j:down,ctrl-k:up"
            ],
            input="\n".join(items),
            text=True,
            capture_output=True
        )

        return result.stdout.strip() or None

    except FileNotFoundError:
        click.echo("Error: 'fzf' or 'bat' is not installed.", err=True)
        return None
