import click
from pathlib import Path
import re
import yaml
from .file_utils import find_all_notes, extract_xrefs, get_front_matter, write_front_matter

def check_broken_links(root_dir: Path):
    """Find and report broken xref links relative to their files."""
    notes = find_all_notes(root_dir)  # {unique_id: Path(file)}
    broken_links = []

    for unique_id, file in notes.items():
        xrefs = extract_xrefs(file)

        for xref in xrefs:
            xref_path = (file.parent / xref).resolve()  # Convert relative xref to absolute

            if not xref_path.exists():
                match = re.search(r"(\d{12})", xref)
                if match:
                    ref_id = match.group(1)
                    correct_path = notes.get(ref_id)

                    if correct_path:
                        broken_links.append((file, xref, correct_path))
                    else:
                        broken_links.append((file, xref, None))

    return broken_links


def fix_broken_links(root_dir: Path, dry_run=False, ask=False):
    """Find and fix broken xref links in AsciiDoc files."""
    broken_links = check_broken_links(root_dir)

    if not broken_links:
        click.secho("✅ No broken links found.", fg="green")
        return

    for file, broken_xref, correct_path in broken_links:
        if correct_path:
            correct_xref = correct_path.relative_to(root_dir).as_posix()
            click.secho(f"\n🔧 Fixing {broken_xref} → {correct_xref} in {file}", fg="yellow")

            if dry_run:
                click.secho("   (Dry run: No changes made.)", fg="blue")
                continue

            if ask and not click.confirm("   Apply this change?", default=False):
                click.secho("   ❌ Skipped.", fg="red")
                continue

            with file.open("r", encoding="utf-8") as f:
                content = f.read()

            new_content = content.replace(f"xref:{broken_xref}", f"xref:{correct_xref}")

            with file.open("w", encoding="utf-8") as f:
                f.write(new_content)

            click.secho("   ✅ Fixed!", fg="green")

    click.secho("\n✅ All broken links processed.", fg="green")


def update_yaml_backlinks(root_dir: Path, dry_run=False, ask=False):
    """Update backlinks in AsciiDoc files if the front matter is valid."""
    # Loop through all .adoc files in the root directory
    notes = find_all_notes(root_dir)
    root_path = root_dir.resolve()

    # Create a dictionary to track backlinks for each note using absolute file paths relative to root
    backlinks_map = {note.resolve().relative_to(root_path): [] for note in notes.values()}

    # First, identify backlinks by scanning all files for xrefs
    for unique_id, file in notes.items():
        # Skip file if it doesn't have valid front matter
        front_matter = get_front_matter(file)
        if not front_matter:
            click.secho(f"❌ Skipping {file} due to empty or faulty front matter.", fg="yellow")
            continue
        
        # Check for xrefs in the current file
        xrefs = extract_xrefs(file)
        
        for xref in xrefs:
            # Resolve the xref file path relative to the root
            xref_path = (file.parent / xref).resolve()

            # Ensure the xref points to a valid file
            if xref_path.exists() and xref_path in notes.values():
                xref_relative = xref_path.relative_to(root_path)
    
                # Only add the backlink if it's a valid file and not the current file
                if xref_relative != file.resolve().relative_to(root_path):
                    backlinks_map[xref_relative].append(file.name)  # Only store the filename, not full path

    # Now, update the backlinks in each file's front matter
    for unique_id, file in notes.items():
        front_matter = get_front_matter(file)
        
        if not front_matter:
            click.secho(f"❌ Skipping {file} due to empty or faulty front matter.", fg="yellow")
            continue
        
        # Check if there are any backlinks to add
        backlinks = front_matter.get('backlinks', [])
        new_backlinks = set(backlinks + backlinks_map.get(file.resolve().relative_to(root_path), []))  # Remove duplicates

        # Only update if backlinks have changed
        if new_backlinks != set(backlinks):
            front_matter['backlinks'] = list(new_backlinks)  # Convert back to list for YAML compatibility
            click.secho(f"✅ Updated backlinks for {file.name}", fg="green")

            # If it's a dry run, don't actually modify the file
            if dry_run:
                click.secho("   (Dry run: No changes made.)", fg="blue")
                continue

            if ask and not click.confirm("   Apply this change?", default=False):
                click.secho("   ❌ Skipped.", fg="red")
                continue

            # Save changes to the file
            write_front_matter(file, front_matter)
            click.secho(f"   ✅ Backlinks updated for {file.name}.", fg="green")

    click.secho("\n✅ All backlinks processed.", fg="green")

# untested
# TODO put into cli
def show_isolated_files(root_dir: Path):
    """Show files that are neither linking to other files nor being linked to by others."""
    notes = find_all_notes(root_dir)
    root_path = root_dir.resolve()
    isolated_files = []

    # Check for files with no backlinks and no xrefs
    for unique_id, file in notes.items():
        # Get the front matter
        front_matter = get_front_matter(file)
        if not front_matter:
            continue  # Skip files with faulty front matter

        # Check backlinks (empty or not present)
        backlinks = front_matter.get('backlinks', [])
        if not backlinks:
            # Check xrefs
            xrefs = extract_xrefs(file)
            if not xrefs:
                # If no backlinks and no xrefs, it's an isolated file
                isolated_files.append(file)

    return isolated_files
