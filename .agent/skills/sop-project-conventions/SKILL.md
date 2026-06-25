---
name: sop-project-conventions
description: Use when starting a new project, creating specs, plans, or any SDLC artifact - enforces SOP-DEV-001 directory structure and naming conventions
---

# SOP Project Conventions

## Overview

Directory structure, naming conventions, and document standards per SOP-DEV-001.

**Core principle:** Every SDLC artifact must be in the correct location with the correct naming convention. No exceptions.

## Directory Structure

```
project-root/
├── docs/superpowers/
│   ├── specs/           # Spec documents (Step 1: Specification)
│   │   └── YYYY-MM-DD-<feature-name>-design.md
│   └── plans/           # Implementation plans (Step 2: Planning)
│       └── YYYY-MM-DD-<feature-name>-plan.md
├── docs/plans/
│   └── task.md          # Task tracker (table-only, continuously updated)
└── .worktrees/          # Isolated git worktrees (Step 3: Environment)
    └── feature-<name>/
```

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Spec | `SPEC-###` | `SPEC-001` |
| User Story | `US-###` | `US-012` |
| Architecture Decision | `ADR-###` | `ADR-003` |
| Task | `TR-###` | `TR-045` |

## Spec Frontmatter

```yaml
---
id: SPEC-001
title: Feature Name
status: draft | reviewed | approved
author: Author Name
date: YYYY-MM-DD
---
```

**Valid `status` values:** `draft` → `reviewed` → `approved`. Only `approved` permits coding.

## Task Granularity

Every task in a plan must:

- Complete in **2-5 minutes**
- Specify **exact file paths** (not "relevant files")
- Include **sample test code** (for coding tasks)
- Include **run command** and **expected output**
- End with `git commit` with a clear message

## Progress Tracking

```markdown
- [ ] Task description    → Not started
- [~] Task description    → In progress
- [x] Task description    → Completed + committed
```

**Rule:** Do not mark `[x]` until `git commit` is done.

## Quick Reference

| Artifact | Location | Example |
|----------|----------|---------|
| Spec | `docs/superpowers/specs/` | `2026-06-25-ocr-pipeline-design.md` |
| Plan | `docs/superpowers/plans/` | `2026-06-25-ocr-pipeline-plan.md` |
| Task tracker | `docs/plans/task.md` | Table-only, continuously updated |
| Worktree | `.worktrees/` | `.worktrees/feature-ocr-pipeline` |

## Common Mistakes

| Wrong | Correct |
|-------|---------|
| Save spec in `docs/plans/` | Save in `docs/superpowers/specs/` |
| Filename without date | `YYYY-MM-DD-<name>-design.md` |
| Task "implement authentication" (too large) | Split into 3-5 tasks of 2-5 minutes each |
| Mark `[x]` before commit | Commit first, mark `[x]` after |
| Worktree on `main` | Create isolated worktree: `.worktrees/feature-<name>` |

## Integration

**Referenced by:**
- `.agent/skills/brainstorming/SKILL.md` — When creating design docs
- `.agent/skills/writing-plans/SKILL.md` — When creating plans
- `.agent/skills/using-git-worktrees/SKILL.md` — When creating worktrees
- `.agent/skills/spec-approval-gate/SKILL.md` — When checking spec paths
