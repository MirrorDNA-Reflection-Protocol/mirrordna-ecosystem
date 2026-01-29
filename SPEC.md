# MirrorDNA Ecosystem Specification

**Version:** 2026-01
**Purpose:** Define canonical structure, metadata rules, discovery semantics, and doc conventions for the MirrorDNA ecosystem.

---

## 1. Ecosystem Concept

An **ecosystem** is defined as a set of interconnected repositories, each representing a module, feature, or tool in MirrorDNA's reflective AI infrastructure.

Each repository MUST adhere to the spec rules below for consistency, discoverability, and automated synchronization.

---

## 2. Canonical Metadata for Repositories

Each repo MUST include the following canonical metadata in its root README or in a `metadata.yml` file:

```yaml
name:               # unique repo name
layer:              # one of: protocol, language, runtime, application, infrastructure, research
status:             # alpha | beta | stable | deprecated
short_description:  # 1-2 sentence purpose
long_description:   # 3-5 bullet explanation
dependencies:       # list of repo names it depends on
core_concepts:      # one or more keywords/concepts
license:            # MIT or inherited
authors:            # list of authors/contributors
tags:               # searchable keywords
```

### 2.1 Metadata Rules

- All fields MUST be present except `deprecated` which is optional.
- The `short_description` MUST NOT exceed 150 characters.
- The `dependencies` array MUST be validated against the canonical ecosystem index.

---

## 3. Layer Definitions

Repositories MUST be assigned into exactly one **layer**:

| Layer | Purpose |
|-------|---------|
| **protocol** | Core identity, reflection rules, semantic anchors |
| **language** | Grammar/ontology/semantic scaffolding |
| **runtime** | Execution, tooling, orchestration |
| **application** | User-facing tools/interfaces |
| **infrastructure** | Deployment, build, CI/CD |
| **research** | Exploratory, non-productized |

---

## 4. README Conventions

Every repo MUST start with:

```markdown
# repo-name

**Layer:** <layer>
**Status:** <status>
**Purpose:** <short_description>
```

Example:

```markdown
# active-mirror-identity

**Layer:** protocol
**Status:** beta
**Purpose:** Generates a portable identity seed for reflective AI.
```

---

## 5. Discoverability Rules

### 5.1 Repo Ordering

In the canonical ecosystem graph, nodes MUST be:

- Placed centrally if they have >= 3 reverse dependencies
- Placed peripherally if they have zero reverse dependencies

This helps AI ranking and visual priority.

### 5.2 Clustering

Repos within the same `layer` MUST be grouped visually together, with clear boundaries.

---

## 6. Graph Semantics

### 6.1 Node Definitions

Each node in the graph MUST include:

```yaml
id:
label: <short_description>
layer:
status:
dependencies:
reverse_dependencies:
weight:
```

### 6.2 Edge Definitions

Edges MUST represent *meaningful relationships*:

```yaml
source:    # child
target:    # parent
type:      # direct | conceptual | test | example
direction: # unidirectional
```

Edge types:

| Type | Meaning |
|------|---------|
| direct | Direct import/invocation |
| conceptual | Explains/inspired by |
| test | Test dependency |
| example | Usage example dependency |

---

## 7. Visual Legend Requirements

The ecosystem graph MUST display a legend with:

- Color -> layer
- Shape -> status
- Size -> inbound dependency weight
- Link -> relationship type

### Colors

| Layer | Color |
|-------|-------|
| protocol | blue |
| language | green |
| runtime | purple |
| application | orange |
| infrastructure | teal |
| research | yellow |

### Shapes

| Status | Shape |
|--------|-------|
| stable | circle |
| beta | diamond |
| alpha | triangle |
| deprecated | cross |

### Link Styles

| Type | Style |
|------|-------|
| direct | solid |
| conceptual | dashed |
| example | dotted |

---

## 8. Readability Rules

- All nodes MUST show labels at zoom level >= 75%
- On hover, nodes MUST display `long_description`
- CLI view MUST expose label and layer

---

## 9. Documentation Cross-References

Repositories MUST include cross-links where relevant:

**Rule:**
```
If repo_A depends on repo_B then:
  A README MUST include a "See also:" link to B
  B README SHOULD include a reciprocal link with context
```

This ensures internal navigation paths for users and AI.

---

## 10. Documentation Automation

AI tooling that syncs docs MUST:

### 10.1 Consistency Checks

- Validate `metadata.yml` fields are present
- Validate cross-repo links are actual URLs
- Validate dependencies in metadata against ecosystem index
- Auto-generate missing dependency listings

### 10.2 Updates

- AI MUST NOT remove user-authored content without a diff review
- AI MAY generate summaries, TOCs, and cross-links
- AI MUST present proposed changes (diff) as a PR

### 10.3 Non-Breaking Criteria

Before merging changes, tests MUST pass:

- All READMEs render successfully
- All cross-links resolve (HTTP 200)
- There are no cyclical direct dependencies (tool error if found)
- Graph generation script runs without errors

---

## 11. AI Sync Workflow (CI)

Every code push to main triggers:

1. AI metadata audit
2. Repo README update proposals
3. Canonical ecosystem index update
4. Dependency graph recompute
5. Graph data JSON regeneration
6. Docs site deploy

### CI Guards

```yaml
on: push to main
jobs:
  metadata_audit:
    # run AI model to validate and propose metadata fixes
  update_docs:
    # runs only if audit reports no blocking errors
```

### Blocking Errors

- Missing metadata.yml fields
- Unresolved cross-links
- Missing layer assignments
- Dependency cycle violation

---

## 12. Testing & Monitoring

AI changelog MUST ALWAYS include:

- What changed
- Why it changed
- Affected repos
- Affected docs

Example:

```
# 2026-01-mirrorDNA update

- Updated README in active-mirror-identity
- Added cross-link to MirrorDNA-Standard
- Standardized metadata format
```

---

## 13. Naming & Tagging Conventions

Use lower-kebab for repos.
Use tags in metadata for search indexing.

Example:
```yaml
tags:
  - reflection
  - identity
  - protocol
  - ai-infrastructure
```

---

## 14. Non-Functional Constraints

### 14.1 Self-Containment

No automated change may:

- Delete user comments
- Rewrite human-crafted docs without review
- Remove historical commit traces

---

## 15. Versioning

Every repo MUST include a `spec_version` in metadata:

```yaml
spec_version: "2026-01"
```

---

## 16. Security / Safety

AI updates MUST NOT:

- Inject executable code without test harness
- Update core logic by inference alone
- Modify sensitive keys or config without explicit approval

---

## 17. Deprecation Rules

A repo should be marked `deprecated` when:

- No active maintenance for 90+ days
- Replaced by newer module
- Documented migration path provided

---

## 18. Onboarding & Quickstart

Docs MUST include:

```markdown
# Quickstart

1. Clone ecosystem index
2. Install graph renderer
3. Run local docs
4. See interactive graph
```

---

## 19. Glossary

| Term | Definition |
|------|------------|
| Ecosystem Index | JSON map of repos, layers, deps |
| Dep Graph | Directed graph representation |
| Metadata | Required repository descriptors |
| AI Sync Bot | Automated sync process |

---

## 20. Acceptance Criteria

The ecosystem is valid if:

- 100% repos with metadata
- No unresolved deps
- Graph renders with legend
- All cross-links exist
- CI runs without errors

---

**END SPEC**
