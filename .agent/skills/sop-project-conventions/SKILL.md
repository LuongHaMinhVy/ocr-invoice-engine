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
├── docs/                # Standard Obsidian Vault
│   ├── 00-Inbox/        # Draft notes, raw information
│   ├── 01-Requirements/ # User Stories (US-###)
│   ├── 02-Design/       # Architecture Decision Records (ADR-###)
│   ├── 03-Specs/        # Spec documents (SPEC-###)
│   ├── 04-Development/  # Plans (PLAN-###) & Task Tracker (task.md)
│   ├── 05-Testing/      # Testing plans, logs, test results (TR-###)
│   ├── 06-Maintenance/  # Deployment, ops, maintenance logs
│   └── 99-Templates/    # Templates and SOPs (e.g. SOP-DEV-001)
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
| Spec | `docs/03-Specs/` | `SPEC-002-ocr-invoice-design.md` |
| Plan | `docs/04-Development/` | `PLAN-002-ocr-invoice-plan.md` |
| Task tracker | `docs/04-Development/task.md` | Table-only, continuously updated |
| Worktree | `.worktrees/` | `.worktrees/feature-ocr-pipeline` |

## Common Mistakes

| Wrong | Correct |
|-------|---------|
| Save spec in `docs/plans/` | Save in `docs/03-Specs/` |
| Filename without SPEC prefix | `SPEC-###-<name>.md` |
| Task "implement authentication" (too large) | Split into 3-5 tasks of 2-5 minutes each |
| Mark `[x]` before commit | Commit first, mark `[x]` after |
| Worktree on `main` | Create isolated worktree: `.worktrees/feature-<name>` |

## Integration

**Referenced by:**
- `.agent/skills/brainstorming/SKILL.md` — When creating design docs
- `.agent/skills/writing-plans/SKILL.md` — When creating plans
- `.agent/skills/using-git-worktrees/SKILL.md` — When creating worktrees
- `.agent/skills/spec-approval-gate/SKILL.md` — When checking spec paths
