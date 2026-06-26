# ADR-001: JWT Authentication, Strict CORS, and API Rate Limiting

**Date:** 2026-06-26
**Status:** Accepted
**Author:** Antigravity (AI Agent)

---

## 1. Context & Problem
Trong thiết kế ban đầu (SAD-001 và SPEC-002), hệ thống OCR Invoice Engine hoạt động ở chế độ không xác thực (unauthenticated), cho phép mọi truy cập local đều có quyền thao tác trực tiếp vào tài nguyên hóa đơn. 

Tuy nhiên, khi phân tích sâu hơn về các mối đe dọa bảo mật (Security Assessment), việc thiếu các cơ chế bảo mật cơ bản như giới hạn nguồn gốc yêu cầu (CORS), giới hạn tần suất gọi API (Rate Limiting), và xác thực người dùng (Authentication) sẽ dẫn đến các rủi ro nghiêm trọng khi đưa lên môi trường Production hoặc mạng nội bộ:
1. **Lạm dụng tài nguyên:** Kẻ xấu có thể spam tải tệp lên để làm cạn kiệt API Key Gemini (phát sinh chi phí lớn) hoặc làm tràn ổ cứng máy chủ.
2. **Lộ thông tin nhạy cảm:** Mọi người dùng trong mạng đều có thể xem và sửa hóa đơn của nhau.
3. **Tấn công Cross-Site:** Thiếu cấu hình CORS chặt chẽ tạo điều kiện cho các trang web độc hại gửi request giả mạo tới backend.

---

## 2. Decision & Deviation Details
Chúng tôi quyết định bổ sung lớp bảo mật nâng cao cho Backend FastAPI và Frontend Next.js trước khi bắt đầu viết code chính thức:
* **JWT Authentication:** Sử dụng JSON Web Tokens (`PyJWT` và `bcrypt` để mã hóa mật khẩu) để bảo vệ tất cả các API nghiệp vụ (upload, xem lịch sử, chi tiết hóa đơn). API kiểm tra sức khỏe `/api/invoices/health` vẫn ở chế độ công khai.
* **Strict CORS Middleware:** Cấu hình FastAPI chỉ chấp nhận các yêu cầu CORS xuất phát từ danh sách whitelist nguồn gốc (đọc từ biến môi trường `ALLOWED_ORIGINS`, mặc định là `http://localhost:3000`).
* **API Rate Limiting:** Sử dụng thư viện `slowapi` tích hợp vào FastAPI để giới hạn số lần gọi các API nhạy cảm (như API đăng nhập và tải hóa đơn) theo từng địa chỉ IP của client.

**Tài liệu bị ảnh hưởng:**
* Bổ sung kế hoạch kiểm thử và code chi tiết trong `docs/04-Development/PLAN-005-security-hardening.md`.
* Sẽ cập nhật phần Phân quyền/Xác thực vào đặc tả kiến trúc `SAD-001` trong tương lai nếu cần thiết.

---

## 3. Rationale & Trade-offs
Quyết định này mang lại sự cân bằng giữa tính bảo mật thực tế và độ phức tạp phát triển:
- **Ưu điểm (Pros):**
  * Bảo vệ API Key Gemini khỏi bị sử dụng chùa hoặc spam phá hoại.
  * Đảm bảo tính riêng tư của dữ liệu hóa đơn giữa các tài khoản khác nhau.
  * Ngăn ngừa các nguy cơ bị tấn công mạng phổ biến (CORS, DoS, brute-force mật khẩu).
- **Nhược điểm (Cons):**
  * Tăng độ phức tạp của codebase ở cả backend (thêm middleware, users table, auth service) và frontend (thêm form đăng nhập, lưu token, axios interceptor).
  * Viết thêm nhiều kịch bản kiểm thử TDD cho các luồng Authentication.

---

## 4. Consequences
- **Đối với Codebase:** 
  * Cần cài thêm các thư viện: `PyJWT`, `bcrypt`, `slowapi`.
  * Cần cấu hình và duy trì thêm bảng `users` trong cơ sở dữ liệu PostgreSQL.
  * Frontend cần có thêm trang Login (`/login`) và cơ chế quản lý trạng thái đăng nhập.
- **Đối với Testing:**
  * Toàn bộ testcase hiện có và viết mới phải gửi kèm Header `Authorization: Bearer <token>` khi gọi các API được bảo vệ.
