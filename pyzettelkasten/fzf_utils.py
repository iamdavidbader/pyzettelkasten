import subprocess
import click

def fzf_select(items, directory = "."):
    """Pipes a list of items to fzf and captures both the query and the selected item."""
    if not items:
        click.echo("No results found.")
        return None, None

    try:
        result = subprocess.run(
            [
                "fzf",
                "--print-query",  # Print the query string before the selected item
                "--preview", "bat --color=always --style=plain --line-range=:100 {}",
                "--bind", "ctrl-o:execute(code {})+abort",  # Open file in VS Code
                "--bind", "ctrl-j:down,ctrl-k:up",  # Enable Vim-style navigation
                "--bind", "ctrl-y:execute-silent(echo {} | clip)+abort"  # Copy filename to clipboard
            ],
            input="\n".join(items),
            text=True,
            capture_output=True,
            cwd=directory
        )

        # Split the output into lines
        output = result.stdout.strip().split("\n")
        print(f"fzf output: {output}")  # Debugging output

        # Handle cases based on the length of the output
        if len(output) == 0:
            # No query and no selection
            return None, None
        elif len(output) == 1:
            # Either a query with no match or a selection with no query
            query_or_selection = output[0]
            if query_or_selection in items:
                # It's a selection
                return None, query_or_selection
            else:
                # It's a query
                return query_or_selection, None
        elif len(output) >= 2:
            # Both query and selection are present
            query = output[0]
            selection = output[1]
            return query, selection

    except FileNotFoundError:
        click.echo("Error: 'fzf' or 'bat' is not installed or not in PATH.", err=True)
        return None, None