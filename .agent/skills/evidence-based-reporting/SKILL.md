---
name: evidence-based-reporting
description: Use when about to claim work is complete or report results - enforces SOP-DEV-001 Iron Law 3 requiring real evidence before any completion claims, in both Vietnamese and English
---

# Evidence-Based Reporting

## Overview

SOP-DEV-001 Iron Law #3: **"Evidence First — Report After"**.

**Core principle:** Every completion claim must include real evidence. No exceptions. No subjective assertions.

**Violating the letter of this rule is violating the spirit.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT EVIDENCE
```

## Forbidden Phrases

These phrases indicate subjective assertion without evidence. **Never use them in completion reports:**

### Vietnamese

- ❌ "Em nghĩ là chạy được rồi" (I think it works)
- ❌ "Hình như xong rồi" (Seems done)
- ❌ "Chắc là ok" (Probably ok)
- ❌ "Theo em thấy thì ổn" (Looks fine to me)
- ❌ "Đáng lẽ phải hoạt động" (Should be working)

### English

- ❌ "should work"
- ❌ "probably works"
- ❌ "seems to be working"
- ❌ "I think it works"
- ❌ "it looks correct"
- ❌ "I believe this is fixed"

### Replace with

- ✅ "Test suite: 42 passed, 0 failed" (with log output)
- ✅ "Linter: 0 errors, 0 warnings" (with log output)
- ✅ "Build: exit code 0" (with log output)

## Required Evidence

Before claiming completion, you **MUST** run and paste output for:

| Check | Command | Expected |
|-------|---------|----------|
| Test suite | `npm test` / `pytest` / `mvn test` | 0 failures |
| Linter | `eslint .` / `flake8` / `checkstyle` | 0 errors |
| Build | `npm run build` / `mvn package` | exit code 0 |

**Rule:** Output must be **actual terminal output**, not a verbal description.

## Audit Criteria (from SOP)

When completing a feature, additionally verify:

- [ ] Test coverage ≥ 85% (or explain why lower)
- [ ] Commit history is clean, each commit maps to 1 task in the plan
- [ ] No leftover code: `grep -r "TODO\|TBD\|FIXME\|HACK" src/`
- [ ] Plan updated: all tasks marked `- [x]`

## Progress Update Rule

```
AFTER EACH TASK COMPLETION:
1. Run tests → paste output
2. git commit -m "feat/fix: <description>"
3. Update plan: - [ ] → - [x]
4. Update task.md: status → done

Do NOT mark [x] without a commit.
Do NOT commit without tests passing.
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'm sure it works" | Certainty ≠ evidence. Run the tests. |
| "I already tested manually" | Manual testing doesn't count. Need automated tests. |
| "Build succeeded" | Build ≠ tests pass. Need both. |
| "It works on my machine" | Need log output, not verbal claims. |
| "Task is small, no need to verify" | Small → fast to verify. Still must verify. |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Too many verification steps" | Each step < 30 seconds. Total < 2 minutes. |
| "Tests aren't written yet" | Then you can't claim completion |
| "CI will run the tests" | CI is backup, not a substitute for local verification |
| "Tight deadline" | Shipping broken code = slower rollback later |

## Integration

**Complements:** `.agent/skills/verification-before-completion/SKILL.md`

The `verification-before-completion` skill enforces the general verification process. This skill adds:
- Forbidden phrases list (Vietnamese + English)
- SOP-DEV-001 audit criteria
- Specific progress update rules

**References:** `.agent/skills/sop-project-conventions/SKILL.md` (task marking conventions)
