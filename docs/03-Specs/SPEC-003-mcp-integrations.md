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

### 2.1 Email Intake (Spring Boot Native IMAP)
The email intake flow runs natively in the Spring Boot backend using a background scheduler.

```
+--------------------+
|  External Email    | (Invoice attachments: PNG, JPG, PDF)
|  Mailbox (IMAP)    |
+---------+----------+
          |
          | Polling (every 5 minutes)
          v
+---------+----------+
| Spring Boot IMAP   |
| Mail Receiver      |
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

- **Configuration:** Cấu hình qua `application.yml` (mail server host, port, username, password, protocol=imaps, folder=INBOX).
- **Security:** Sử dụng TLS/SSL để kết nối với mail server.
- **Handling:** Lọc chỉ lấy email có tệp đính kèm dạng hình ảnh (`image/*`) hoặc PDF (`application/pdf`). Sau khi xử lý xong, đánh dấu thư là đã đọc (Read) hoặc di chuyển thư vào thư mục `processed/` để tránh xử lý lặp lại.

### 2.2 PostgreSQL Database MCP
Dành riêng cho quá trình phát triển và kiểm tra dữ liệu bằng Agent:
- **Server:** `@modelcontextprotocol/server-postgres`
- **Cấu hình kết nối:** Kết nối trực tiếp đến PostgreSQL database của dự án (`jdbc:postgresql://localhost:5432/ocr_invoice`).
- **Khả năng hỗ trợ:** Agent có thể chạy các tool của Postgres MCP để:
  - Xem danh sách bảng (`list_tables`).
  - Xem schema của bảng hóa đơn (`describe_table`).
  - Thực thi các câu lệnh SELECT để đối chiếu dữ liệu trích xuất thực tế (`query`).

---

## 3. Tech Stack
- **Backend:** `org.springframework.boot:spring-boot-starter-integration`, `org.springframework.integration:spring-integration-mail`, `com.sun.mail:jakarta.mail`.
- **Database MCP:** Node.js, `@modelcontextprotocol/server-postgres`.

---

## 4. Error Handling
- **Mail Server Connection Failures:** Ghi log lỗi và tự động retry ở chu kỳ poll tiếp theo. Không làm sập ứng dụng.
- **Invalid File Formats:** Nếu file đính kèm không phải định dạng ảnh hoặc PDF được hỗ trợ, bỏ qua và ghi log cảnh báo.
- **Duplication Prevention:** Sử dụng mã Message-ID của email để lưu vết, đảm bảo mỗi email chỉ được xử lý đúng 1 lần.
