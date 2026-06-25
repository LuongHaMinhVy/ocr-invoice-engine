---
name: spec-approval-gate
description: Use when about to write production code for any feature or bugfix - enforces SOP-DEV-001 rule that no code is written without an approved spec
---

# Spec Approval Gate

## Overview

SOP-DEV-001 Iron Law #1: **"No Spec, No Code"**.

**Core principle:** No production code may be written until a spec with `status: approved` exists. No exceptions.

**Violating the letter of this rule is violating the spirit.**

## The Iron Law

```
NO PRODUCTION CODE WITHOUT APPROVED SPEC
```

If the Gate Check is not complete, you may not write code.

## When to Use

- Before writing production code for a new feature
- Before fixing a bug that changes logic
- Before architectural refactoring

**Not required for:** Typo fixes, documentation updates, minor config changes with no logic impact.

## The Gate Check

```
BEFORE WRITING CODE:

1. Find the related spec in `docs/03-Specs/`
   → No spec found? STOP. Create the spec first.

2. Read frontmatter `status:`
   → Not `approved`? STOP. Get the spec approved first.

3. Verify AI-Ready Checklist:
   - [ ] Clear scope (input/output/boundary defined)
   - [ ] Contract or interface definition exists
   - [ ] Expected test cases listed (at least happy path + 1 edge case)
   - [ ] No placeholders ("TBD", "TODO", "will add later")
   → Checklist incomplete? STOP. Complete the spec.

4. All passed → Log which spec was approved → Proceed to code.
```

## Red Flags

If you find yourself thinking:

| Thought | Reality |
|---------|---------|
| "This feature is simple, no spec needed" | Simple features still need clear scope |
| "Just a quick fix" | Quick fixes without spec = quick tech debt |
| "The spec is implicitly understood" | Implicit = everyone understands differently |
| "Write code first, spec later" | Code-first = spec is forced to match, losing its purpose |
| "We already discussed it" | Discussion without written spec = no spec |
| "It's just a prototype" | Prototypes need scope too. No scope = prototype becomes production |

**All of these mean: STOP. Create/approve the spec first.**

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Feature is too small" | Small → short spec. Still needs one. |
| "Tight deadline" | Having a spec = faster coding, less rework |
| "I already understand the requirements" | Understanding ≠ documenting. Spec = documented for verification |
| "Spec takes too much time" | Wrong code takes more time than writing a spec |

## Integration

**Runs before:** `.agent/skills/test-driven-development/SKILL.md`

**Runs after:** `.agent/skills/writing-plans/SKILL.md` (plan must reference spec)

**References:** `.agent/skills/sop-project-conventions/SKILL.md` (spec file paths)
