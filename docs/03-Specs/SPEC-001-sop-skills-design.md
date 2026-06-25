# SOP-DEV-001 Skills — Thiết kế

> **Ngày:** 2026-06-25
> **Trạng thái:** Approved
> **Mục tiêu:** Bổ sung 3 skills mới cho Antigravity Superpowers để enforce quy trình SOP-DEV-001

---

## Bối cảnh

Dự án sử dụng quy trình SOP-DEV-001 ("QUY TRÌNH ÁP DỤNG AI TRONG DỰ ÁN") và phương pháp luận từ khóa AI-Driven SDLC. Bộ 13 skills mặc định từ `superpowers` đã có nền tảng tốt (TDD, verification, git worktrees...) nhưng thiếu 3 điểm đặc thù của SOP.

## 3 Gap cần lấp

| Gap | Mô tả | Điều luật SOP |
|-----|--------|---------------|
| A | Không có skill enforce cổng duyệt spec (`status: approved`) trước khi code | Điều luật #1 |
| B | Đường dẫn thư mục/quy ước đặt tên chưa đồng bộ với SOP | Quy trình 5 bước |
| C | Thiếu quy tắc "bằng chứng trước — báo cáo sau" bằng tiếng Việt | Điều luật #3 |

## Quyết định

**Cách A:** 3 skills nhỏ, mỗi cái giải 1 gap. Không sửa 13 skills hiện có.

## Skill 1: `spec-approval-gate`

- **Trigger:** Agent sắp viết code production
- **Hành vi:** Kiểm `status: approved` trong spec → DỪNG nếu chưa duyệt
- **Checklist AI-Ready:** rõ phạm vi, có contract, có test cases, không placeholder
- **Tương tác:** Chạy trước `test-driven-development`, sau `writing-plans`

## Skill 2: `sop-project-conventions`

- **Trigger:** Bắt đầu dự án, tạo spec, tạo plan
- **Enforce:** Đường dẫn SOP (`docs/superpowers/specs/`, `docs/superpowers/plans/`), mã định danh, task 2-5 phút, worktree conventions
- **Tương tác:** Tham chiếu bởi `brainstorming`, `writing-plans`, `using-git-worktrees`

## Skill 3: `evidence-based-reporting`

- **Trigger:** Agent sắp tuyên bố hoàn thành
- **Quy tắc:** Cấm cụm từ cảm tính (VN+EN), buộc log test + linter, tiêu chí audit SOP
- **Tương tác:** Bổ sung cho `verification-before-completion`

## Đánh đổi

- Thêm 3 file nhưng mỗi file nhỏ gọn (<200 words)
- Không sửa skills hiện có → không rủi ro regression
- Skills mới tham chiếu (không force-load) skills hiện có
