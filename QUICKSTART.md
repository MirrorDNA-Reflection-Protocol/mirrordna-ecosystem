# Quickstart

Get oriented in 60 seconds.

## See the Ecosystem (30 seconds)

```bash
git clone https://github.com/MirrorDNA-Reflection-Protocol/mirrordna-ecosystem
cd mirrordna-ecosystem
cat ecosystem-index.json | jq '.layers'
```

Output:
```json
{
  "protocol": { "count": 8 },
  "language": { "count": 3 },
  "runtime": { "count": 12 },
  "application": { "count": 6 },
  "infrastructure": { "count": 5 },
  "research": { "count": 21 }
}
```

## Explore a Layer

```bash
# See all protocol-layer repos
cat ecosystem-index.json | jq '.repos[] | select(.layer == "protocol") | .name'
```

## Run a Local Mirror (60 seconds)

The fastest demo:

```bash
# Visit the live sovereign inference demo
open https://activemirror.ai/mirror
```

This runs Llama 3.3 70B through MirrorGate — sovereign inference, no cloud memory.

## Create Your First Memory Seed

```bash
# Generate a portable AI identity
open https://id.activemirror.ai
```

Follow the prompts. Your seed stays local — nothing stored on servers.

## Next Steps

| What you want | Where to go |
|---------------|-------------|
| Understand the architecture | [SPEC.md](SPEC.md) |
| Read the full story | [STORY.md](STORY.md) |
| See repo dependencies | [ecosystem-index.json](ecosystem-index.json) |
| Add metadata to your fork | [templates/metadata.yml.template](templates/metadata.yml.template) |

## Key Repos to Clone

If you want to run the stack locally:

```bash
# Core protocol
git clone https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA

# Runtime orchestration
git clone https://github.com/MirrorDNA-Reflection-Protocol/MirrorBrain

# Inference control
git clone https://github.com/MirrorDNA-Reflection-Protocol/mirrorgate

# MCP tools
git clone https://github.com/MirrorDNA-Reflection-Protocol/mirrordna-mcp
```

---

Questions? Open an issue or read [SPEC.md](SPEC.md) for technical details.
