import click
from pathlib import Path
import yaml
import os
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
    return config.get('notes_directory', '.')

@click.group()
@click.option("--directory", "-d", type=click.Path(exists=True, file_okay=False, readable=True), 
              default=get_notes_directory(), show_default=True, help="Root directory containing notes.")
@click.pass_context
def cli(ctx, directory):
    """CLI for managing notes and tags."""
    ctx.obj = {"directory": Path(directory)}

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
        selected = fzf_select(files)
        if selected:
            click.echo(f"Selected file: {selected}")
    else:
        click.echo("\n".join(map(str, files)))

if __name__ == "__main__":
    cli()
