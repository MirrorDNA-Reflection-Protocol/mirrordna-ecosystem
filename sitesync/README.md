# SiteSync — Ecosystem Property Synchronization

> Keeps all Active Mirror properties in sync with canonical branding, stats, and links.

## What This Does

**Problem:** With 88 repos and 7+ live properties, branding drift, stale stats, and broken links are inevitable.

**Solution:** SiteSync provides:
1. **inventory.json** — Single source of truth for all domains, repos, and pages
2. **audit.py** — Scans for violations and generates reports
3. **templates/** — Canonical header/footer components

## Quick Start

```bash
# Run full audit
python sitesync/audit.py

# Check specific aspect
python sitesync/audit.py --branding
python sitesync/audit.py --links
python sitesync/audit.py --stats

# Output as JSON
python sitesync/audit.py --json > audit-report.json
```

## Inventory Structure

```json
{
  "domains": {
    "primary": [...],      // activemirror.ai, id.*, brief.*
    "github_pages": [...], // Documentation sites
    "reserved": [...]      // Future domains
  },
  "pages": {...},          // All pages per domain
  "repos": {...},          // Repos by category
  "branding": {...},       // Canonical colors, tagline, copyright
  "health_endpoints": [...] // URLs to health check
}
```

## What Gets Audited

### Branding Violations
- Old company name references
- Missing ⟡ glyph in titles
- Wrong domain (.com vs .ai)
- Outdated copyright years

### Stale Statistics
- Repo counts that don't match reality
- Old dates in content
- Outdated user/download numbers

### Broken Links
- Dead internal file references
- Missing assets
- Typos in paths

## Canonical Templates

### Header (`templates/header.html`)
- Protocol banner: "Part of the Active MirrorOS ecosystem"
- Minimal cross-site navigation
- Responsive styles included

### Footer (`templates/footer.html`)
- Brand attribution
- Legal links (Trust, Privacy, Terms)
- Copyright: "© 2026 N1 Intelligence (OPC) Pvt Ltd"
- Ecosystem badge

## Integration

Copy templates directly or use as reference. The styles are self-contained.

For React/JSX:
```jsx
// Convert HTML templates to JSX components
// See activemirror-site/src/components/Footer.jsx for example
```

## CI Integration

Add to GitHub Actions:
```yaml
- name: SiteSync Audit
  run: python sitesync/audit.py
  continue-on-error: true  # Report issues, don't block
```

## Files

```
sitesync/
├── README.md           # This file
├── inventory.json      # All properties and metadata
├── audit.py            # Audit tool
└── templates/
    ├── header.html     # Canonical header
    └── footer.html     # Canonical footer
```

---

*Part of the MirrorDNA Ecosystem management layer.*
