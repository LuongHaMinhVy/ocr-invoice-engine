# Obsidian Vault Restructuring Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Reorganize the project's documentation folder (`docs/`) into a standard Obsidian Vault structure (with the 8 standard folders) and update the skills and references to maintain consistency with the new conventions.

**Architecture:** Create standard vault folders inside `docs/`, relocate initial education and SOP files, move design specs and implementation plans to their correct folders, and rewrite the skill files in `.agent/skills/` to point to the correct paths.

**Tech Stack:** Bash/PowerShell commands, Markdown, Git.

---

### Task 1: Create Standard Vault Folders

**Files:**
- Create: `docs/00-Inbox/.gitkeep`
- Create: `docs/01-Requirements/.gitkeep`
- Create: `docs/02-Design/.gitkeep`
- Create: `docs/03-Specs/.gitkeep`
- Create: `docs/04-Development/.gitkeep`
- Create: `docs/05-Testing/.gitkeep`
- Create: `docs/06-Maintenance/.gitkeep`
- Create: `docs/99-Templates/.gitkeep`

**Step 1: Create directories**
Run:
```powershell
mkdir docs/00-Inbox, docs/01-Requirements, docs/02-Design, docs/03-Specs, docs/04-Development, docs/05-Testing, docs/06-Maintenance, docs/99-Templates
```
Expected: Folders created successfully.

**Step 2: Create .gitkeep files to allow tracking empty folders**
Run:
```powershell
New-Item -Path docs/00-Inbox/.gitkeep, docs/01-Requirements/.gitkeep, docs/02-Design/.gitkeep, docs/03-Specs/.gitkeep, docs/04-Development/.gitkeep, docs/05-Testing/.gitkeep, docs/06-Maintenance/.gitkeep, docs/99-Templates/.gitkeep -ItemType File -Force
```
Expected: `.gitkeep` files created.

**Step 3: Commit**
```bash
git add docs/00-Inbox/ docs/01-Requirements/ docs/02-Design/ docs/03-Specs/ docs/04-Development/ docs/05-Testing/ docs/06-Maintenance/ docs/99-Templates/
git commit -m "chore: initialize standard obsidian vault directory structure in docs/"
```

---

### Task 2: Relocate Initial Files and Current Design Docs

**Files:**
- Modify: Move `QUY TRÌNH ÁP DỤNG AI TRONG DỰ ÁN.md` to `docs/99-Templates/SOP-DEV-001-Quy-trinh-AI.md`
- Modify: Move `ELEARNING-SINHVIEN.html` to `docs/ELEARNING-SINHVIEN.html`
- Modify: Move `docs/superpowers/specs/2026-06-25-ocr-invoice-design.md` to `docs/03-Specs/SPEC-002-ocr-invoice-design.md`
- Modify: Move `docs/superpowers/plans/2026-06-25-ocr-invoice-plan.md` to `docs/04-Development/PLAN-002-ocr-invoice-plan.md`

**Step 1: Relocate and rename files via Git**
Run:
```powershell
git mv "QUY TRÌNH ÁP DỤNG AI TRONG DỰ ÁN.md" "docs/99-Templates/SOP-DEV-001-Quy-trinh-AI.md"
git mv "ELEARNING-SINHVIEN.html" "docs/ELEARNING-SINHVIEN.html"
git mv "docs/superpowers/specs/2026-06-25-ocr-invoice-design.md" "docs/03-Specs/SPEC-002-ocr-invoice-design.md"
git mv "docs/superpowers/plans/2026-06-25-ocr-invoice-plan.md" "docs/04-Development/PLAN-002-ocr-invoice-plan.md"
```
Expected: Files moved successfully without loss of history.

**Step 2: Clean up old empty directories**
Run:
```powershell
Remove-Item -Recurse -Force docs/superpowers
```
Expected: The old `docs/superpowers/` directory is removed.

**Step 3: Commit**
```bash
git add docs/
git commit -m "chore: relocate initial files and current specs/plans to the new vault structure"
```

---

### Task 3: Update Project Conventions Skill to Enforce New Paths

**Files:**
- Modify: `.agent/skills/sop-project-conventions/SKILL.md`

**Step 1: Check existing path rules in skill**
Run:
```powershell
Select-String -Path .agent/skills/sop-project-conventions/SKILL.md -Pattern "superpowers"
```
Expected: Shows occurrences of `docs/superpowers/specs/` and `docs/superpowers/plans/`.

**Step 2: Update conventions to new paths**
Modify `.agent/skills/sop-project-conventions/SKILL.md` to replace the old directory structure:
- Specs location: `docs/03-Specs/`
- Plans location: `docs/04-Development/`
- Requirements location: `docs/01-Requirements/`
- Design/ADRs location: `docs/02-Design/`
- Inbox location: `docs/00-Inbox/`
- Templates/SOP location: `docs/99-Templates/`

**Step 3: Verify the changes**
Run: `cat .agent/skills/sop-project-conventions/SKILL.md` and check the directory tree section.
Expected: The directories match the new standard.

**Step 4: Commit**
```bash
git add .agent/skills/sop-project-conventions/SKILL.md
git commit -m "feat: update sop-project-conventions skill with new vault directory structure"
```

---

### Task 4: Update Spec Approval Gate Skill to Validate New Paths

**Files:**
- Modify: `.agent/skills/spec-approval-gate/SKILL.md`

**Step 1: Check existing path logic in spec gate**
Run:
```powershell
Select-String -Path .agent/skills/spec-approval-gate/SKILL.md -Pattern "superpowers"
```
Expected: Shows logic enforcing specs must reside in `docs/superpowers/specs/`.

**Step 2: Update gate logic**
Modify `.agent/skills/spec-approval-gate/SKILL.md` to check that new specs are located in `docs/03-Specs/`.

**Step 3: Verify the changes**
Run: `cat .agent/skills/spec-approval-gate/SKILL.md` to check the updated paths.
Expected: Paths point to `docs/03-Specs/`.

**Step 4: Commit**
```bash
git add .agent/skills/spec-approval-gate/SKILL.md
git commit -m "feat: update spec-approval-gate skill to check docs/03-Specs/"
```

---

### Task 5: Fix Internal References in Relocated Docs

**Files:**
- Modify: `docs/03-Specs/SPEC-002-ocr-invoice-design.md`
- Modify: `docs/04-Development/PLAN-002-ocr-invoice-plan.md`

**Step 1: Search for old folder references in files**
Run:
```powershell
Select-String -Path docs/03-Specs/SPEC-002-ocr-invoice-design.md, docs/04-Development/PLAN-002-ocr-invoice-plan.md -Pattern "superpowers"
```
Expected: List of lines with old references.

**Step 2: Replace old paths with new paths**
Update `docs/03-Specs/SPEC-002-ocr-invoice-design.md` and `docs/04-Development/PLAN-002-ocr-invoice-plan.md` to replace references of `docs/superpowers/plans/` with `docs/04-Development/` and `docs/superpowers/specs/` with `docs/03-Specs/`.

**Step 3: Commit**
```bash
git add docs/03-Specs/SPEC-002-ocr-invoice-design.md docs/04-Development/PLAN-002-ocr-invoice-plan.md
git commit -m "chore: fix internal references to relocated docs paths"
```
