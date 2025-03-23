import click
from pathlib import Path
import yaml
import os
import subprocess
from datetime import datetime
from jinja2 import Template
from .file_utils import find_all_notes, get_tags_from_meta_data, get_front_matter
from .fzf_utils import fzf_select
from .link_checker import fix_broken_links, update_backlinks, show_isolated_files

# Load configuration from YAML file
config_path = Path(os.path.expanduser("~/.config/pyzettelkasten/config.yaml"))
if config_path.exists():
    with config_path.open('r') as config_file:
        config = yaml.safe_load(config_file)
else:
    config = {}

def get_notes_directory():
    return Path(config.get('notes_directory', '.'))

def get_editor():
    return config.get('editor', 'notepad')  # Default to notepad if no editor is specified

def get_template(template_name):
    templates_dir = Path(config.get('templates_directory', './templates'))
    template_path = templates_dir / f"{template_name}.adoc"
    if template_path.exists():
        with template_path.open('r') as template_file:
            return template_file.read()
    return ""

@click.group()
@click.option("--directory", "-d", type=click.Path(exists=True, file_okay=False, readable=True), 
              default=get_notes_directory(), show_default=True, help="Root directory containing notes.")
@click.pass_context
def cli(ctx, directory):
    """CLI for managing notes and tags."""
    ctx.obj = {"directory": Path(directory)}

@cli.command()
@click.pass_context
@click.argument("title", required=False)
@click.option("-i", "--interactive", is_flag=True, help="Use fzf for selection")
@click.option("-t", "--template", default="note", help="Template to use for the new note")
def note(ctx, title, interactive, template):
    """Create or open a note with a timestamped filename."""
    directory = ctx.obj["directory"]

    if interactive:
        # Find all files
        files = [str(file) for file in directory.glob("*.adoc")]
        query, selected = fzf_select(files)
        if selected:
            filepath = Path(selected)
            click.echo(f"Selected file: {filepath}")
        elif query:
            click.echo(query)
            # Use the query string to create a new note
            title = query
        else:
            click.echo("No file selected and no input provided.")
            return
    else:
        if not title:
            click.echo("Title is required when not using interactive mode.")
            return
    if title:
        # Create a new note if no file was selected
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"{timestamp}-{title.replace(' ', '-').lower()}.adoc"
        filepath = directory / filename

    if not filepath.exists():
        template_content = get_template(template)
        rendered_content = Template(template_content).render(title=title, now=datetime.now())
        with filepath.open('w') as note_file:
            note_file.write(rendered_content)

    # Open the file in the specified editor
    editor = get_editor()
    try:
        subprocess.run([editor, str(filepath)], check=True)
    except FileNotFoundError:
        click.echo(f"Error: The specified editor '{editor}' was not found. Please ensure it is installed and in your PATH.", err=True)

@cli.command()
@click.pass_context
@click.option("-i", "--interactive", is_flag=True, help="Use fzf for selection")
def all_tags(ctx, interactive):
    """List all tags."""
    directory = ctx.obj["directory"]
    tags = set()
    for file in find_all_notes(directory).values():
        tags.update(get_tags_from_meta_data(get_front_matter(file)))

    tags = sorted(tags)

    if interactive:
        selected = fzf_select(tags)
        if selected:
            click.echo(f"Selected tag: {selected}")
    else:
        click.echo("\n".join(tags))

@cli.command()
@click.pass_context
@click.argument("tag")
@click.option("-i", "--interactive", is_flag=True, help="Use fzf for selection")
def tag(ctx, tag, interactive):
    """List files with a specific tag."""
    directory = ctx.obj["directory"]
    files = [
        str(file)
        for file in find_all_notes(directory).values()
        if tag in get_tags_from_meta_data(get_front_matter(file))
    ]

    if interactive:
        selected = fzf_select(files)
        if selected:
            click.echo(f"Selected file: {selected}")
    else:
        click.echo("\n".join(files))

@cli.command()
@click.pass_context
@click.option("-i", "--interactive", is_flag=True, help="Use fzf for selection")
def tagless(ctx, interactive):
    """List files that have no tags."""
    directory = ctx.obj["directory"]
    files = [
        str(file)
        for file in find_all_notes(directory).values()
        if not get_tags_from_meta_data(get_front_matter(file))
    ]

    if interactive:
        selected = fzf_select(files)
        if selected:
            click.echo(f"Selected file: {selected}")
    else:
        click.echo("\n".join(files))

@cli.command()
@click.pass_context
@click.option("--dry-run", is_flag=True, help="Preview changes without modifying files")
@click.option("--ask", is_flag=True, help="Ask before applying each fix")
def fix_links(ctx, dry_run, ask):
    """Find and fix broken xref links in AsciiDoc files."""
    directory = ctx.obj["directory"]
    fix_broken_links(directory, dry_run, ask)
    update_backlinks(directory, dry_run)

@cli.command()
@click.pass_context
@click.option("-i", "--interactive", is_flag=True, help="Use fzf for selection")
def isolated(ctx, interactive):
    """Show files that are neither linking to other files nor being linked to by others."""
    directory = ctx.obj["directory"]
    files = show_isolated_files(directory)

    if interactive:
        selected = fzf_select([str(file) for file in files])
        if selected:
            click.echo(f"Selected file: {selected}")
    else:
        click.echo("\n".join(map(str, files)))

if __name__ == "__main__":
    cli()
