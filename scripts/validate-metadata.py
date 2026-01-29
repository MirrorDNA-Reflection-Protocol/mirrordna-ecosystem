#!/usr/bin/env python3
"""
validate-metadata.py - Validates metadata.yml files against the spec

Checks:
- Required fields present
- Valid layer values
- Valid status values
- short_description under 150 chars
- Dependencies exist in ecosystem
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Set, List

REPO_ROOT = Path(__file__).parent.parent
ECOSYSTEM_INDEX = REPO_ROOT / "ecosystem-index.json"

REQUIRED_FIELDS = [
    "name", "layer", "status", "short_description",
    "dependencies", "license", "tags", "spec_version"
]

VALID_LAYERS = ["protocol", "language", "runtime", "application", "infrastructure", "research"]
VALID_STATUSES = ["alpha", "beta", "stable", "archived", "deprecated"]

def load_ecosystem_repos() -> Set[str]:
    """Load known repo names from ecosystem index."""
    if not ECOSYSTEM_INDEX.exists():
        return set()
    with open(ECOSYSTEM_INDEX) as f:
        data = json.load(f)
    return {r["name"] for r in data.get("repos", [])}

def validate_metadata(metadata_path: Path, known_repos: Set[str]) -> List[str]:
    """Validate a single metadata.yml file."""
    errors = []

    try:
        with open(metadata_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["metadata.yml must be a YAML object"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate layer
    if "layer" in data and data["layer"] not in VALID_LAYERS:
        errors.append(f"Invalid layer '{data['layer']}'. Must be one of: {VALID_LAYERS}")

    # Validate status
    if "status" in data and data["status"] not in VALID_STATUSES:
        errors.append(f"Invalid status '{data['status']}'. Must be one of: {VALID_STATUSES}")

    # Validate short_description length
    if "short_description" in data:
        desc = str(data["short_description"]).strip()
        if len(desc) > 150:
            errors.append(f"short_description exceeds 150 chars ({len(desc)} chars)")

    # Validate dependencies exist
    if "dependencies" in data and known_repos:
        for dep in data.get("dependencies", []):
            if dep not in known_repos:
                errors.append(f"Unknown dependency: {dep}")

    # Validate tags is a list
    if "tags" in data and not isinstance(data["tags"], list):
        errors.append("tags must be a list")

    return errors

def main():
    """Validate all metadata.yml files in repos directory."""
    repos_dir = Path.home() / "repos"
    known_repos = load_ecosystem_repos()

    total_checked = 0
    total_errors = 0
    repos_with_errors = []

    print("Validating metadata.yml files...\n")

    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue

        metadata_file = repo_dir / "metadata.yml"
        if not metadata_file.exists():
            continue

        total_checked += 1
        errors = validate_metadata(metadata_file, known_repos)

        if errors:
            total_errors += len(errors)
            repos_with_errors.append(repo_dir.name)
            print(f"[FAIL] {repo_dir.name}")
            for error in errors:
                print(f"       - {error}")
        else:
            print(f"[OK]   {repo_dir.name}")

    print(f"\n{'='*50}")
    print(f"Checked: {total_checked} repos")
    print(f"Errors:  {total_errors}")
    print(f"Failed:  {len(repos_with_errors)} repos")

    if repos_with_errors:
        sys.exit(1)
    else:
        print("\nAll metadata files valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()
