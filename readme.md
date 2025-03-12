# pyzettelkasten

`pyzettelkasten` is a CLI tool for managing Zettelkasten notes.

I used this project to test the capabilities of GPTs.
Most of the code is written using GPT-4o.

## Installation

You can install the package using `pip`:

```sh
pip install .
```

## Usage

### CLI Commands

- `all_tags`: List all tags.
- `tag <tag>`: List files with a specific tag.
- `tagless`: List files that have no tags.
- `fix_links`: Find and fix broken xref links in AsciiDoc files.
- `isolated`: Show files that are neither linking to other files nor being linked to by others.

### Example

```sh
# List all tags
pyzettelkasten all_tags

# List files with a specific tag
pyzettelkasten tag mytag

# List files that have no tags
pyzettelkasten tagless

# Find and fix broken xref links in AsciiDoc files
pyzettelkasten fix_links

# Show files that are neither linking to other files nor being linked to by others
pyzettelkasten isolated
```

## Configuration

You can configure the directory of your notes using a YAML configuration file located at `~/.config/.pyzettel/config.yaml`:

```yaml
notes_directory: /path/to/your/notes
```

## License

This project is licensed under the MIT License.