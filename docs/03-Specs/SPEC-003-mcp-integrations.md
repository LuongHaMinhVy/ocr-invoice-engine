---
id: SPEC-003
title: Email Intake & PostgreSQL Database MCP Integrations
status: approved
author: Antigravity
date: 2026-06-25
---

# SPEC-003: Email Intake & PostgreSQL Database MCP Integrations

## 1. Goal
Provide automated intake of invoice files via email mailbox polling and allow direct database inspection for verification using PostgreSQL MCP during development and operation.

## 2. Architecture & Data Flow

### 2.1 Email Intake (Python Native IMAP)
The email intake flow runs natively in the FastAPI backend using a background scheduler (APScheduler).

```
+--------------------+
|  External Email    | (Invoice attachments: PNG, JPG, PDF)
|  Mailbox (IMAP)    |
+---------+----------+
          |
          | Polling (every 5 minutes)
          v
+---------+----------+
|   Python IMAP      |
|  Mail Receiver      |
+---------+----------+
          |
          | Extracts attachments
          v
+---------+----------+
| Temp File Staging  | (Creates local temporary files)
+---------+----------+
          |
          | Sends to Invoice OCR Pipeline
          v
+---------+----------+      +--------------------+
|  OCR Processing    | ---> | Save to Postgres   |
|  (Gemini API)      |      +--------------------+
+--------------------+
```

- **Configuration:** Cấu hình qua `.env` (mail server host, port, username, password, protocol=imaps, folder=INBOX).
- **Security:** Sử dụng TLS/SSL để kết nối với mail server.
- **Handling:** Lọc chỉ lấy email có tệp đính kèm dạng hình ảnh (`image/*`) hoặc PDF (`application/pdf`). Sau khi xử lý xong, đánh dấu thư là đã đọc (Read) hoặc di chuyển thư vào thư mục `processed/` để tránh xử lý lặp lại.

### 2.2 PostgreSQL Database MCP
Dành riêng cho quá trình phát triển và kiểm tra dữ liệu bằng Agent:
- **Server:** `@modelcontextprotocol/server-postgres`
- **Cấu hình kết nối:** Kết nối trực tiếp đến PostgreSQL database của dự án (`postgresql://localhost:5432/ocr_invoice`).
- **Khả năng hỗ trợ:** Agent có thể chạy các tool của Postgres MCP để:
  - Xem danh sách bảng (`list_tables`).
  - Xem schema của bảng hóa đơn (`describe_table`).
  - Thực thi các câu lệnh SELECT để đối chiếu dữ liệu trích xuất thực tế (`query`).

### 2.3 Hermes MCP Notification Integration
Backend FastAPI gửi thông báo tự động thông qua việc gửi yêu cầu HTTP POST tới REST bridge của Hermes MCP hoặc gọi trực tiếp công cụ `messages_send` để đẩy tin nhắn qua Telegram/Slack:
- **Cấu hình Target:** Đọc từ biến môi trường `HERMES_NOTIFICATION_TARGET` (ví dụ: `telegram:-1002148765432` hoặc `slack:#invoice-notifications`).
- **Nội dung tin nhắn:**
  ```
  🔔 [OCR Invoice] Phát hiện hóa đơn mới!
  - Nhà cung cấp: {vendor}
  - Tổng tiền: {total} VNĐ
  - Trạng thái xác thực: {status}
  - Link đối chiếu: http://localhost:3000/invoices/{id}
  ```
- **Resilience:** Nếu Hermes REST bridge không phản hồi, ghi nhận Error Log cảnh báo mà không làm sập luồng xử lý chính.

---

## 3. Tech Stack
- **Backend:** Python Standard Library `imaplib`, `email`, `requests` (cho việc gọi REST API tới Hermes bridge), và `APScheduler`.
- **Database MCP:** Node.js, `@modelcontextprotocol/server-postgres`.

---

## 4. Error Handling
- **Mail Server Connection Failures:** Ghi log lỗi và tự động retry ở chu kỳ poll tiếp theo. Không làm sập ứng dụng.
- **Invalid File Formats:** Nếu file đính kèm không phải định dạng ảnh hoặc PDF được hỗ trợ, bỏ qua và ghi log cảnh báo.
- **Duplication Prevention:** Sử dụng mã Message-ID của email để lưu vết, đảm bảo mỗi email chỉ được xử lý đúng 1 lần.
