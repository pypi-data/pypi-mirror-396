#!/usr/bin/env python3
"""Command-line interface for lu."""

import os
import sys
import json
import argparse
from typing import Dict, List, Any

try:
    import yaml
except ImportError:
    yaml = None


def load_config(yaml_file: str = 'lu.yaml') -> Dict[str, Any]:
    """Load configuration from lu.yaml file."""
    if yaml is None:
        print("Error: PyYAML is required. Install it with: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(yaml_file):
        print(f"Error: Configuration file '{yaml_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(yaml_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print(f"Error: YAML file must contain a dictionary.", file=sys.stderr)
        sys.exit(1)

    return config


def remove_recordings(pattern: str, yaml_file: str = 'lu.yaml') -> None:
    """Remove recordings that match the given pattern.

    Args:
        pattern: String pattern to search for in recording entries
        yaml_file: Path to the YAML configuration file
    """
    config = load_config(yaml_file)

    # Get manifest file path from config
    recordings_dir = config.get('recordings_dir')
    if not recordings_dir:
        print("Error: 'recordings_dir' not found in configuration.", file=sys.stderr)
        sys.exit(1)

    manifest_file = config.get('manifest_file')
    if not manifest_file:
        manifest_file = os.path.join(recordings_dir, 'recordings.json')

    if not os.path.exists(manifest_file):
        print(f"Warning: Manifest file '{manifest_file}' not found. Nothing to remove.")
        return

    # Load manifest
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if not isinstance(manifest, dict):
        print("Error: Manifest file must contain a dictionary.", file=sys.stderr)
        sys.exit(1)

    # Find entries to remove
    entries_to_remove = []
    files_to_remove = []

    for entry_id, entry_data in manifest.items():
        # Convert entry to string representation for searching
        entry_str = json.dumps(entry_data, sort_keys=True)

        if pattern in entry_str or pattern in entry_id:
            entries_to_remove.append(entry_id)
            file_path = entry_data.get('file')
            if file_path:
                files_to_remove.append(file_path)

    if not entries_to_remove:
        print(f"No recordings found matching pattern: '{pattern}'")
        return

    print(f"Found {len(entries_to_remove)} recording(s) matching pattern: '{pattern}'")

    # Remove physical files
    removed_files = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  Removed file: {file_path}")
                removed_files += 1
            except Exception as e:
                print(f"  Warning: Could not remove file '{file_path}': {e}", file=sys.stderr)
        else:
            print(f"  File not found (skipping): {file_path}")

    # Remove entries from manifest
    for entry_id in entries_to_remove:
        del manifest[entry_id]

    # Write updated manifest
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, sort_keys=True, ensure_ascii=False)

    print(f"\nRemoved {len(entries_to_remove)} entry(ies) from manifest")
    print(f"Removed {removed_files} physical file(s)")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='lu - vcr-style record/replay stubbing library',
        prog='lu'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Remove command
    remove_parser = subparsers.add_parser(
        'remove',
        help='Remove recordings matching a pattern'
    )
    remove_parser.add_argument(
        'pattern',
        help='Pattern to search for in recordings (matches entry IDs and entry data)'
    )
    remove_parser.add_argument(
        '--config',
        default='lu.yaml',
        help='Path to configuration file (default: lu.yaml)'
    )

    args = parser.parse_args()

    if args.command == 'remove':
        remove_recordings(args.pattern, args.config)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
