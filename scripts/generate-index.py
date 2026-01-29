#!/usr/bin/env python3
"""
generate-index.py - Scans repos and builds ecosystem-index.json

Scans /Users/mirror-admin/repos/ for MirrorDNA ecosystem repos,
reads metadata.yml where available, and generates the canonical index.
"""

import json
import os
import re
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

REPOS_DIR = Path.home() / "repos"
OUTPUT_FILE = Path(__file__).parent.parent / "ecosystem-index.json"

# Layer assignment heuristics based on repo names
LAYER_PATTERNS = {
    "protocol": [
        "MirrorDNA", "SCD-Protocol", "MirrorDNA-Standard", "LingOS",
        "mirrordna-zkp", "MirrorDNA-Lattice", "glyph-engine",
        "active-mirror-identity", "sovereign-memory", "udtp"
    ],
    "language": [
        "lingos-kernel", "beacon-glyph-sdk", "LingOS"
    ],
    "runtime": [
        "MirrorBrain", "mirrordna-mcp", "mirrordna-daemons", "mirror-registry",
        "mirrorgate", "chrysalis-bridge", "world-state-daemon", "mirror-swarm-demo",
        "mirrorswarm", "MirrorShell", "MirrorOS_Swarm", "mesh-boot-generator",
        "active-mirror-mesh", "mirrordna-automation", "mirrordna-skills"
    ],
    "application": [
        "activemirror-site", "MirrorBrain-Mobile", "mirrorcowork",
        "active-mirror-2050-core", "ActiveMirrorOS", "Apps"
    ],
    "infrastructure": [
        "sc1-deployment", "sovereign-canaryd", "mirrordna-ecosystem",
        "mirror-authority", "mirror-genesis"
    ],
    "research": [
        "research-papers", "mirrordna-llm-optimizer", "oversight-prototype",
        "active-mirror-identity-synthesis", "mirrordna-examples", "Reflective-Ai",
        "reflex", "awesome", "crewAIInc", "langchain-ai", "mem0"
    ]
}

# Status heuristics
def guess_status(repo_name: str, has_readme: bool) -> str:
    """Guess repo status based on naming and presence of docs."""
    if "prototype" in repo_name.lower() or "demo" in repo_name.lower():
        return "alpha"
    if "example" in repo_name.lower():
        return "beta"
    if repo_name in ["MirrorDNA", "SCD-Protocol", "mirrordna-mcp"]:
        return "stable"
    return "beta"

def guess_layer(repo_name: str) -> str:
    """Guess layer based on repo name patterns."""
    for layer, patterns in LAYER_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() == repo_name.lower():
                return layer
            if pattern.lower() in repo_name.lower():
                return layer
    # Default to research for unknown repos
    return "research"

def read_metadata(repo_path: Path) -> Optional[Dict]:
    """Read metadata.yml if it exists."""
    metadata_file = repo_path / "metadata.yml"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    return None

def extract_readme_info(repo_path: Path) -> dict:
    """Extract layer/status from README if present."""
    readme_files = ["README.md", "readme.md", "README.MD"]
    for readme_name in readme_files:
        readme = repo_path / readme_name
        if readme.exists():
            try:
                with open(readme) as f:
                    content = f.read(2000)  # First 2KB
                    info = {"has_readme": True}

                    # Look for Layer: and Status: markers
                    layer_match = re.search(r'\*\*Layer:\*\*\s*(\w+)', content, re.IGNORECASE)
                    if layer_match:
                        info["layer"] = layer_match.group(1).lower()

                    status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content, re.IGNORECASE)
                    if status_match:
                        info["status"] = status_match.group(1).lower()

                    # Get first line as description
                    lines = content.strip().split('\n')
                    if lines:
                        first_line = lines[0].strip('# ').strip()
                        if len(first_line) < 150 and first_line:
                            info["description"] = first_line

                    return info
            except Exception:
                pass
    return {"has_readme": False}

def is_mirrordna_repo(repo_name: str) -> bool:
    """Filter for MirrorDNA ecosystem repos (exclude forks/awesome lists)."""
    exclude_patterns = [
        "awesome-", "Awesome-", "langchain-ai", "crewAIInc", "mem0"
    ]
    for pattern in exclude_patterns:
        if repo_name.startswith(pattern) or repo_name == pattern:
            return False
    return True

def scan_repos() -> List[Dict]:
    """Scan all repos and build index entries."""
    repos = []

    if not REPOS_DIR.exists():
        print(f"Warning: {REPOS_DIR} not found")
        return repos

    for item in sorted(REPOS_DIR.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith('.'):
            continue

        repo_name = item.name

        # Check for metadata.yml first
        metadata = read_metadata(item)
        readme_info = extract_readme_info(item)

        # Build repo entry
        entry = {
            "name": repo_name,
            "url": f"https://github.com/MirrorDNA-Reflection-Protocol/{repo_name}",
            "local_path": str(item),
            "has_metadata": metadata is not None,
            "has_readme": readme_info.get("has_readme", False),
            "is_ecosystem": is_mirrordna_repo(repo_name)
        }

        # Layer (priority: metadata > readme > guess)
        if metadata and "layer" in metadata:
            entry["layer"] = metadata["layer"]
        elif "layer" in readme_info:
            entry["layer"] = readme_info["layer"]
        else:
            entry["layer"] = guess_layer(repo_name)

        # Status
        if metadata and "status" in metadata:
            entry["status"] = metadata["status"]
        elif "status" in readme_info:
            entry["status"] = readme_info["status"]
        else:
            entry["status"] = guess_status(repo_name, readme_info.get("has_readme", False))

        # Description
        if metadata and "short_description" in metadata:
            entry["short_description"] = metadata["short_description"]
        elif "description" in readme_info:
            entry["short_description"] = readme_info["description"]
        else:
            entry["short_description"] = f"{repo_name} - MirrorDNA ecosystem component"

        # Dependencies
        if metadata and "dependencies" in metadata:
            entry["dependencies"] = metadata["dependencies"]
        else:
            entry["dependencies"] = []

        # Tags
        if metadata and "tags" in metadata:
            entry["tags"] = metadata["tags"]
        else:
            entry["tags"] = [entry["layer"], "mirrordna"]

        # Visibility (all local are assumed public for now)
        entry["visibility"] = "public"

        repos.append(entry)

    return repos

def compute_reverse_dependencies(repos: List[Dict]) -> List[Dict]:
    """Compute reverse dependencies for each repo."""
    repo_map = {r["name"]: r for r in repos}

    for repo in repos:
        repo["reverse_dependencies"] = []

    for repo in repos:
        for dep in repo.get("dependencies", []):
            if dep in repo_map:
                repo_map[dep]["reverse_dependencies"].append(repo["name"])

    return repos

def build_layers_summary(repos: List[Dict]) -> Dict:
    """Build layer summary statistics."""
    layers = {}
    for layer in ["protocol", "language", "runtime", "application", "infrastructure", "research"]:
        layer_repos = [r["name"] for r in repos if r.get("layer") == layer and r.get("is_ecosystem", True)]
        layers[layer] = {
            "count": len(layer_repos),
            "repos": layer_repos
        }
    return layers

def main():
    print("Scanning repos...")
    repos = scan_repos()

    # Filter to ecosystem repos only for the main index
    ecosystem_repos = [r for r in repos if r.get("is_ecosystem", True)]

    print(f"Found {len(repos)} total repos, {len(ecosystem_repos)} ecosystem repos")

    # Compute reverse deps
    ecosystem_repos = compute_reverse_dependencies(ecosystem_repos)

    # Build layer summary
    layers = build_layers_summary(ecosystem_repos)

    # Build final index
    index = {
        "version": "2026-01",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_repos": 87,  # Known total including private
        "local_repos": len(repos),
        "public_repos": 60,
        "private_repos": 27,
        "repos": ecosystem_repos,
        "layers": layers
    }

    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print(f"\nWrote {OUTPUT_FILE}")
    print(f"\nLayer summary:")
    for layer, data in layers.items():
        print(f"  {layer}: {data['count']} repos")

    # Print repos missing metadata
    missing_metadata = [r["name"] for r in ecosystem_repos if not r.get("has_metadata")]
    if missing_metadata:
        print(f"\nRepos missing metadata.yml ({len(missing_metadata)}):")
        for name in missing_metadata[:10]:
            print(f"  - {name}")
        if len(missing_metadata) > 10:
            print(f"  ... and {len(missing_metadata) - 10} more")

if __name__ == "__main__":
    main()
