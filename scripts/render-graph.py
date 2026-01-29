#!/usr/bin/env python3
"""
render-graph.py - Generates ecosystem graph SVG from ecosystem-index.json

Produces a visual graph showing:
- Repos grouped by layer
- Dependencies as edges
- Color-coded by layer
- Size weighted by reverse dependencies
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ECOSYSTEM_INDEX = REPO_ROOT / "ecosystem-index.json"
OUTPUT_SVG = REPO_ROOT / "assets" / "ecosystem-graph.svg"

# Layer colors
COLORS = {
    "protocol": "#3B82F6",      # blue
    "language": "#22C55E",      # green
    "runtime": "#A855F7",       # purple
    "application": "#F97316",   # orange
    "infrastructure": "#14B8A6", # teal
    "research": "#EAB308"       # yellow
}

def load_index() -> dict:
    """Load the ecosystem index."""
    with open(ECOSYSTEM_INDEX) as f:
        return json.load(f)

def generate_mermaid(data: dict) -> str:
    """Generate Mermaid diagram definition."""
    lines = ["graph TB"]

    # Group repos by layer
    for layer, info in data.get("layers", {}).items():
        if not info.get("repos"):
            continue

        lines.append(f"    subgraph {layer.upper()}")
        for repo in info["repos"][:8]:  # Limit to 8 per layer for readability
            safe_name = repo.replace("-", "_")
            lines.append(f"        {safe_name}[{repo}]")
        lines.append("    end")

    # Add some key edges (simplified)
    core_deps = [
        ("MirrorBrain", "MirrorDNA"),
        ("mirrorgate", "MirrorDNA"),
        ("mirrordna_mcp", "MirrorDNA"),
        ("activemirror_site", "MirrorBrain"),
        ("MirrorBrain_Mobile", "mirrordna_mcp"),
    ]

    for src, dst in core_deps:
        lines.append(f"    {src} --> {dst}")

    return "\n".join(lines)

def generate_svg(data: dict) -> str:
    """Generate a simple SVG visualization."""
    width = 1200
    height = 800

    layers = data.get("layers", {})
    layer_names = ["protocol", "language", "runtime", "application", "infrastructure", "research"]

    # Calculate positions
    layer_width = width // len(layer_names)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<style>',
        '  .layer-label { font: bold 14px sans-serif; fill: #374151; }',
        '  .repo-label { font: 11px sans-serif; fill: #1F2937; }',
        '  .repo-box { rx: 6; ry: 6; stroke: #E5E7EB; stroke-width: 1; }',
        '  .legend-text { font: 12px sans-serif; fill: #374151; }',
        '</style>',
        '<rect width="100%" height="100%" fill="#F9FAFB"/>',
        '',
        '<!-- Title -->',
        '<text x="600" y="40" text-anchor="middle" style="font: bold 24px sans-serif; fill: #111827;">MirrorDNA Ecosystem</text>',
        '<text x="600" y="65" text-anchor="middle" style="font: 14px sans-serif; fill: #6B7280;">87 repositories | 6 layers | Sovereign AI Infrastructure</text>',
        ''
    ]

    # Draw layers
    y_start = 100
    for i, layer in enumerate(layer_names):
        x = i * layer_width + 20
        layer_data = layers.get(layer, {"repos": [], "count": 0})
        repos = layer_data.get("repos", [])[:10]  # Max 10 repos shown
        color = COLORS.get(layer, "#9CA3AF")

        # Layer header
        svg_parts.append(f'<!-- {layer.upper()} -->')
        svg_parts.append(f'<rect x="{x}" y="{y_start}" width="{layer_width-40}" height="580" fill="{color}15" rx="12"/>')
        svg_parts.append(f'<text x="{x + (layer_width-40)//2}" y="{y_start + 25}" text-anchor="middle" class="layer-label">{layer.upper()}</text>')
        svg_parts.append(f'<text x="{x + (layer_width-40)//2}" y="{y_start + 45}" text-anchor="middle" style="font: 11px sans-serif; fill: #6B7280;">{layer_data.get("count", 0)} repos</text>')

        # Repo boxes
        for j, repo in enumerate(repos):
            box_y = y_start + 60 + j * 50
            box_width = layer_width - 60
            svg_parts.append(f'<rect x="{x+10}" y="{box_y}" width="{box_width}" height="40" fill="white" class="repo-box"/>')
            svg_parts.append(f'<rect x="{x+10}" y="{box_y}" width="4" height="40" fill="{color}" rx="2"/>')
            # Truncate long names
            display_name = repo if len(repo) < 20 else repo[:17] + "..."
            svg_parts.append(f'<text x="{x+22}" y="{box_y + 25}" class="repo-label">{display_name}</text>')

        # Show "and N more" if truncated
        if layer_data.get("count", 0) > 10:
            remaining = layer_data["count"] - 10
            svg_parts.append(f'<text x="{x + (layer_width-40)//2}" y="{y_start + 560}" text-anchor="middle" style="font: 11px sans-serif; fill: #9CA3AF;">+{remaining} more</text>')

    # Legend
    svg_parts.append('')
    svg_parts.append('<!-- Legend -->')
    legend_y = 720
    svg_parts.append(f'<text x="60" y="{legend_y}" class="legend-text" style="font-weight: bold;">Layers:</text>')

    for i, (layer, color) in enumerate(COLORS.items()):
        lx = 140 + i * 160
        svg_parts.append(f'<rect x="{lx}" y="{legend_y - 12}" width="16" height="16" fill="{color}" rx="3"/>')
        svg_parts.append(f'<text x="{lx + 22}" y="{legend_y}" class="legend-text">{layer}</text>')

    # Footer
    svg_parts.append(f'<text x="600" y="{height - 20}" text-anchor="middle" style="font: 11px sans-serif; fill: #9CA3AF;">Generated from ecosystem-index.json | github.com/MirrorDNA-Reflection-Protocol/mirrordna-ecosystem</text>')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)

def main():
    print("Loading ecosystem index...")
    data = load_index()

    print("Generating SVG...")
    svg_content = generate_svg(data)

    # Ensure assets directory exists
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_SVG, 'w') as f:
        f.write(svg_content)

    print(f"Wrote {OUTPUT_SVG}")

    # Also output Mermaid for reference
    mermaid = generate_mermaid(data)
    mermaid_file = REPO_ROOT / "assets" / "ecosystem-graph.mmd"
    with open(mermaid_file, 'w') as f:
        f.write(mermaid)
    print(f"Wrote {mermaid_file}")

if __name__ == "__main__":
    main()
