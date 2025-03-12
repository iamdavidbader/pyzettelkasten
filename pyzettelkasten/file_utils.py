import yaml
import re
from pathlib import Path

# Regex patterns
XREF_PATTERN = re.compile(r"xref:([\w\-/\.]+)")
ID_PATTERN = re.compile(r"(\d{12})")  # Unique timestamp ID (yyyyMMddhhmm)

# Regular expression to match YAML front matter at the start of the file
FRONT_MATTER_REGEX = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def get_front_matter(file_path: Path):
    """Extract the YAML front matter from an AsciiDoc file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()

        match = FRONT_MATTER_REGEX.match(content)
        if match:
            yaml_content = match.group(1)
            return yaml.safe_load(yaml_content) or {}  # Ensure we return a dictionary

    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")

    return {}  # Return empty dictionary if no valid front matter is found


def write_front_matter(file_path: Path, meta_data: dict):
    """Update the YAML front matter in an AsciiDoc file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()

        new_yaml = yaml.dump(meta_data, default_flow_style=False, sort_keys=False).strip()

        if FRONT_MATTER_REGEX.match(content):
            # Replace existing YAML front matter
            new_content = FRONT_MATTER_REGEX.sub(f"---\n{new_yaml}\n---\n", content, count=1)
        else:
            # Add front matter if not present
            new_content = f"---\n{new_yaml}\n---\n\n{content}"

        with file_path.open("w", encoding="utf-8") as f:
            f.write(new_content)

    except Exception as e:
        print(f"⚠️ Error writing {file_path}: {e}")


def get_tags_from_meta_data(meta_data):
    """Extract tags from YAML front-matter."""
    tags = meta_data.get("tags", [])
    return tags.split() if isinstance(tags, str) else tags


def find_all_notes(root_dir):
    """Find all AsciiDoc files and map unique ID → full path."""
    note_map = {}

    for file in Path(root_dir).rglob("*.adoc"):
        match = ID_PATTERN.search(file.stem)
        if match:
            note_map[match.group(1)] = file

    return note_map


def extract_xrefs(file_path):
    """Extract all xref links from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return XREF_PATTERN.findall(f.read())
    except Exception:
        return []
