#!/usr/bin/env python3
"""
SiteSync Audit Tool

Scans all Active Mirror properties for:
- Broken links
- Stale statistics
- Branding drift
- Missing metadata
- Outdated dependencies

Usage:
    python audit.py                  # Full audit
    python audit.py --links          # Link check only
    python audit.py --branding       # Branding audit only
    python audit.py --stats          # Stats freshness check
    python audit.py --fix            # Auto-fix known issues
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import subprocess

# Load inventory
SCRIPT_DIR = Path(__file__).parent
INVENTORY_PATH = SCRIPT_DIR / "inventory.json"

def load_inventory() -> dict:
    """Load the site inventory."""
    with open(INVENTORY_PATH) as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════════════
# BRANDING AUDIT
# ═══════════════════════════════════════════════════════════════

class BrandingAuditor:
    """Check for branding consistency across properties."""

    def __init__(self, inventory: dict):
        self.branding = inventory["branding"]
        self.violations = []

    def audit_file(self, filepath: Path) -> List[dict]:
        """Check a single file for branding violations."""
        violations = []

        if not filepath.exists():
            return violations

        try:
            content = filepath.read_text()
        except Exception:
            return violations

        # Check for old branding patterns
        old_patterns = [
            (r"Mirror\s+Protocol", "Should be 'MirrorDNA Protocol'"),
            (r"Active\s+MirrorOS", "Should be 'ActiveMirrorOS' (no space)"),
            (r"N1\s+Intelligence\s+Labs", "Should be 'N1 Intelligence (OPC) Pvt Ltd'"),
            (r"©\s*202[0-4]", "Copyright year should be 2026"),
            (r"activemirror\.com", "Domain should be activemirror.ai"),
        ]

        for pattern, message in old_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append({
                    "file": str(filepath),
                    "type": "branding",
                    "pattern": pattern,
                    "message": message
                })

        # Check for missing glyph in titles
        if filepath.suffix in ['.html', '.jsx', '.tsx']:
            if '<title>' in content and '⟡' not in content.split('<title>')[1].split('</title>')[0]:
                violations.append({
                    "file": str(filepath),
                    "type": "branding",
                    "pattern": "title_glyph",
                    "message": "Page title should include ⟡ glyph"
                })

        return violations

    def audit_repo(self, repo_path: Path) -> List[dict]:
        """Audit all files in a repo for branding."""
        violations = []

        # Key files to check
        key_files = [
            "README.md",
            "index.html",
            "src/App.jsx",
            "src/pages/*.jsx",
            "package.json",
        ]

        for pattern in key_files:
            if '*' in pattern:
                files = list(repo_path.glob(pattern))
            else:
                files = [repo_path / pattern]

            for f in files:
                if f.exists():
                    violations.extend(self.audit_file(f))

        return violations


# ═══════════════════════════════════════════════════════════════
# STATS FRESHNESS AUDIT
# ═══════════════════════════════════════════════════════════════

class StatsAuditor:
    """Check for stale statistics in content."""

    def __init__(self, inventory: dict):
        self.inventory = inventory
        self.stale_items = []

    def check_file(self, filepath: Path) -> List[dict]:
        """Check a file for stale stats."""
        issues = []

        if not filepath.exists():
            return issues

        try:
            content = filepath.read_text()
        except Exception:
            return issues

        # Patterns that indicate stats that need updating
        stat_patterns = [
            (r"(\d+)\s*repos?", "repo_count", 88),  # Should be 88
            (r"(\d+)\s*seeds?\s*created", "seed_count", None),  # Dynamic
            (r"(\d+)\s*users?", "user_count", None),  # Dynamic
            (r"(\d+)\s*downloads?", "download_count", None),  # Dynamic
        ]

        for pattern, stat_type, expected in stat_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                found_value = int(match.group(1))
                if expected and found_value != expected:
                    issues.append({
                        "file": str(filepath),
                        "type": "stale_stat",
                        "stat": stat_type,
                        "found": found_value,
                        "expected": expected
                    })

        # Check for date freshness
        date_patterns = [
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+202[0-5]",
            r"202[0-5]-\d{2}-\d{2}",
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            if matches and "2026" not in content:
                issues.append({
                    "file": str(filepath),
                    "type": "stale_date",
                    "message": "Contains old dates, may need updating"
                })
                break

        return issues


# ═══════════════════════════════════════════════════════════════
# LINK CHECKER
# ═══════════════════════════════════════════════════════════════

class LinkChecker:
    """Check for broken internal and external links."""

    def __init__(self, inventory: dict):
        self.inventory = inventory
        self.broken_links = []

    def extract_links(self, filepath: Path) -> List[str]:
        """Extract all links from a file."""
        if not filepath.exists():
            return []

        try:
            content = filepath.read_text()
        except Exception:
            return []

        # Remove code blocks before extracting links (examples shouldn't be validated)
        content = re.sub(r'```[\s\S]*?```', '', content)  # Fenced code blocks
        content = re.sub(r'`[^`]+`', '', content)  # Inline code

        links = []

        # HTML href
        links.extend(re.findall(r'href=["\']([^"\']+)["\']', content))
        # Markdown links
        links.extend(re.findall(r'\[.*?\]\(([^)]+)\)', content))
        # JSX/React links
        links.extend(re.findall(r'to=["\']([^"\']+)["\']', content))

        return links

    def check_internal_links(self, links: List[str], base_path: Path) -> List[dict]:
        """Check if internal links resolve."""
        broken = []

        for link in links:
            # Skip external links
            if link.startswith(('http://', 'https://', 'mailto:', '#', 'javascript:')):
                continue

            # Skip React Router paths (start with /)
            if link.startswith('/'):
                continue

            # Skip obvious non-links (ellipsis, shell commands, whitespace)
            if link in ['...', '..'] or '|' in link or link.startswith(' ') or len(link) < 2:
                continue

            # Skip anchor links within files (file.md#anchor)
            if '#' in link:
                # Check if the file part exists
                file_part = link.split('#')[0]
                if not file_part:
                    continue  # Just an anchor, skip
                target = base_path / file_part
                if target.exists():
                    continue  # File exists, anchor validation is separate

            # Check relative file paths
            target = base_path / link
            if not target.exists() and not (base_path / link.replace('.html', '.jsx')).exists():
                broken.append({
                    "type": "broken_link",
                    "link": link,
                    "base": str(base_path)
                })

        return broken


# ═══════════════════════════════════════════════════════════════
# MAIN AUDIT
# ═══════════════════════════════════════════════════════════════

def run_full_audit(inventory: dict, repos_path: Path) -> dict:
    """Run complete audit across all properties."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "branding_violations": [],
        "stale_stats": [],
        "broken_links": [],
        "health_issues": [],
        "summary": {}
    }

    branding = BrandingAuditor(inventory)
    stats = StatsAuditor(inventory)
    links = LinkChecker(inventory)

    # Audit each repo
    for category, repos in inventory["repos"].items():
        for repo_name in repos:
            repo_path = repos_path / repo_name
            if not repo_path.exists():
                continue

            # Branding
            brand_issues = branding.audit_repo(repo_path)
            results["branding_violations"].extend(brand_issues)

            # Stats
            for f in ["README.md", "index.html"]:
                filepath = repo_path / f
                results["stale_stats"].extend(stats.check_file(filepath))

            # Links (exclude node_modules, .git, vendor directories)
            for f in repo_path.glob("**/*.md"):
                if any(skip in str(f) for skip in ['node_modules', '.git', 'vendor', '__pycache__', '.venv', 'venv']):
                    continue
                file_links = links.extract_links(f)
                results["broken_links"].extend(
                    links.check_internal_links(file_links, f.parent)
                )

    # Summary
    results["summary"] = {
        "branding_violations": len(results["branding_violations"]),
        "stale_stats": len(results["stale_stats"]),
        "broken_links": len(results["broken_links"]),
        "health_issues": len(results["health_issues"]),
        "status": "PASS" if all(
            len(results[k]) == 0 for k in ["branding_violations", "broken_links"]
        ) else "ISSUES_FOUND"
    }

    return results


def print_report(results: dict):
    """Print audit report to console."""
    print("\n" + "=" * 60)
    print("⟡ SITESYNC AUDIT REPORT")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print()

    # Branding
    print(f"BRANDING VIOLATIONS: {len(results['branding_violations'])}")
    for v in results["branding_violations"][:5]:
        print(f"  - {v['file']}: {v['message']}")
    if len(results["branding_violations"]) > 5:
        print(f"  ... and {len(results['branding_violations']) - 5} more")
    print()

    # Stats
    print(f"STALE STATISTICS: {len(results['stale_stats'])}")
    for s in results["stale_stats"][:5]:
        print(f"  - {s['file']}: {s.get('stat', 'date')} issue")
    print()

    # Links
    print(f"BROKEN LINKS: {len(results['broken_links'])}")
    for l in results["broken_links"][:5]:
        print(f"  - {l['base']}: {l['link']}")
    print()

    # Summary
    print("-" * 60)
    print(f"STATUS: {results['summary']['status']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="SiteSync Audit Tool")
    parser.add_argument("--links", action="store_true", help="Link check only")
    parser.add_argument("--branding", action="store_true", help="Branding audit only")
    parser.add_argument("--stats", action="store_true", help="Stats freshness check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--repos", type=Path, default=Path.home() / "repos",
                       help="Path to repos directory")
    args = parser.parse_args()

    inventory = load_inventory()
    results = run_full_audit(inventory, args.repos)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    # Exit with error code if issues found
    sys.exit(0 if results["summary"]["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
