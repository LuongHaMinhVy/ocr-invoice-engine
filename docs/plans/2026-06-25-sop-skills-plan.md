# SOP-DEV-001 Skills Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Tạo 3 skills mới (`spec-approval-gate`, `sop-project-conventions`, `evidence-based-reporting`) để enforce quy trình SOP-DEV-001 trong Antigravity.

**Architecture:** Mỗi skill là 1 thư mục trong `.agent/skills/` chứa file `SKILL.md`. Skills mới tham chiếu (không force-load) các skills hiện có. Tuân thủ cấu trúc và best practices từ `writing-skills`.

**Tech Stack:** Markdown (SKILL.md files), YAML frontmatter

---

### Task 1: Tạo skill `spec-approval-gate`

**Files:**
- Create: `.agent/skills/spec-approval-gate/SKILL.md`

**Step 1: Tạo thư mục skill**

```bash
mkdir -p .agent/skills/spec-approval-gate
```

**Step 2: Viết SKILL.md**

Tạo file `.agent/skills/spec-approval-gate/SKILL.md` với nội dung:

- YAML frontmatter: `name: spec-approval-gate`, `description: Use when about to write production code for any feature or bugfix - enforces SOP-DEV-001 rule that no code is written without an approved spec`
- Overview: Điều luật #1 SOP — "KHÔNG CÓ SPEC, KHÔNG CÓ CODE"
- The Iron Law: `NO PRODUCTION CODE WITHOUT APPROVED SPEC`
- The Gate Function: 5 bước kiểm tra (tìm spec → đọc status → kiểm checklist AI-Ready → cho phép/chặn)
- Checklist AI-Ready (từ M6): rõ phạm vi, có contract, có test cases, không placeholder
- Bảng Red Flags: "Viết code trước spec", "Spec vẫn draft", "Spec có placeholder"
- Bảng Rationalization: "Tính năng đơn giản", "Sửa nhanh thôi", "Spec ngầm hiểu"
- Integration: chạy trước `test-driven-development`, sau `writing-plans`

**Step 3: Kiểm tra file**

Run: `cat .agent/skills/spec-approval-gate/SKILL.md | head -5`
Expected: Thấy YAML frontmatter đúng

**Step 4: Commit**

```bash
git add .agent/skills/spec-approval-gate/SKILL.md
git commit -m "feat: add spec-approval-gate skill (SOP Điều luật #1)"
```

---

### Task 2: Tạo skill `sop-project-conventions`

**Files:**
- Create: `.agent/skills/sop-project-conventions/SKILL.md`

**Step 1: Tạo thư mục skill**

```bash
mkdir -p .agent/skills/sop-project-conventions
```

**Step 2: Viết SKILL.md**

Tạo file `.agent/skills/sop-project-conventions/SKILL.md` với nội dung:

- YAML frontmatter: `name: sop-project-conventions`, `description: Use when starting a new project, creating specs, plans, or any SDLC artifact - enforces SOP-DEV-001 directory structure and naming conventions`
- Overview: Quy ước thư mục và đặt tên theo SOP-DEV-001
- Bảng Directory Conventions: specs → `docs/superpowers/specs/YYYY-MM-DD-<tên>-design.md`, plans → `docs/superpowers/plans/YYYY-MM-DD-<tên>-plan.md`
- Naming Conventions: `SPEC-###`, `US-###`, `ADR-###`, `TR-###`
- Task Granularity: 2-5 phút, ghi rõ file path + code test mẫu + lệnh chạy
- Progress Tracking: `- [ ]` → `- [x]` + git commit sau mỗi task
- Worktree: `.worktrees/feature-<tên-tính-năng>`
- Quick Reference table
- Integration: tham chiếu bởi `brainstorming`, `writing-plans`, `using-git-worktrees`

**Step 3: Kiểm tra file**

Run: `cat .agent/skills/sop-project-conventions/SKILL.md | head -5`
Expected: Thấy YAML frontmatter đúng

**Step 4: Commit**

```bash
git add .agent/skills/sop-project-conventions/SKILL.md
git commit -m "feat: add sop-project-conventions skill (SOP directory & naming)"
```

---

### Task 3: Tạo skill `evidence-based-reporting`

**Files:**
- Create: `.agent/skills/evidence-based-reporting/SKILL.md`

**Step 1: Tạo thư mục skill**

```bash
mkdir -p .agent/skills/evidence-based-reporting
```

**Step 2: Viết SKILL.md**

Tạo file `.agent/skills/evidence-based-reporting/SKILL.md` với nội dung:

- YAML frontmatter: `name: evidence-based-reporting`, `description: Use when about to claim work is complete or report results - enforces SOP-DEV-001 Iron Law 3 requiring real evidence before any completion claims, in both Vietnamese and English`
- Overview: Điều luật #3 SOP — "BẰNG CHỨNG TRƯỚC — BÁO CÁO SAU"
- The Iron Law: `KHÔNG BÁO CÁO KHI CHƯA CÓ BẰNG CHỨNG`
- Forbidden Phrases (VN): "Em nghĩ là chạy được rồi", "Hình như xong rồi", "Chắc là ok"
- Forbidden Phrases (EN): "should", "probably", "seems to", "I think it works"
- Required Evidence: test suite output (`0 failures`), linter output (`0 errors`), build success (exit 0)
- Audit Criteria (từ SOP): test coverage ≥85%, commit history rõ ràng theo plan, không code thừa (TODO/TBD)
- Progress Update Rule: cập nhật `- [x]` trong plan + `git commit` sau mỗi task hoàn thành
- Bảng Red Flags + Rationalization
- Integration: bổ sung cho `verification-before-completion`

**Step 3: Kiểm tra file**

Run: `cat .agent/skills/evidence-based-reporting/SKILL.md | head -5`
Expected: Thấy YAML frontmatter đúng

**Step 4: Commit**

```bash
git add .agent/skills/evidence-based-reporting/SKILL.md
git commit -m "feat: add evidence-based-reporting skill (SOP Điều luật #3)"
```

---

### Task 4: Tạo task tracker và commit toàn bộ

**Files:**
- Create/Update: `docs/plans/task.md`

**Step 1: Cập nhật task tracker**

Cập nhật `docs/plans/task.md` đánh dấu tất cả task hoàn thành.

**Step 2: Commit final**

```bash
git add docs/plans/
git commit -m "docs: add SOP skills design doc, plan, and task tracker"
```
