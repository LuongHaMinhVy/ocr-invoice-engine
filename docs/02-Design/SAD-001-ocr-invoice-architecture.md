# System Architecture Design (SAD)
## Dự án: Hệ thống tự động hóa Thu thập và Đối chiếu Hóa đơn (OCR Invoice Engine)

| Phiên bản | Ngày | Người thực hiện | Trạng thái |
|---|---|---|---|
| v1.0 | 2026-06-26 | Antigravity | Hoàn thành dự thảo |

---

## 1. Kiến trúc Tổng quan (System Architecture Overview)

Hệ thống được thiết kế theo mô hình **Monorepo** chia sẻ mã nguồn nhưng phân tách triển khai độc lập giữa **Apps/Backend** và **Apps/Frontend**, kết hợp với các cổng giao tiếp kết nối hệ thống bên ngoài thông qua kiến trúc **Hexagonal Architecture (Ports and Adapters)** ở Backend.

### 1.1 Sơ đồ Phân rã Thành phần (Component Diagram)

```mermaid
graph TD
    subgraph "Next.js Frontend (apps/frontend)"
        UI[Interactive UI Pages]
        API_Client[REST Client / Axios]
        UI --> API_Client
    end

    subgraph "Flask Backend (apps/backend)"
        direction TB
        subgraph "Primary Adapters (Inbound)"
            REST[Invoice REST Blueprint]
            Email_Poller[IMAP Email Intake Poller]
        end

        subgraph "Application Core"
            Biz_Processor[Invoice Processing Service]
            OCR_Manager[Gemini OCR Client Service]
            Math_Validator[Validation Engine]
            
            REST & Email_Poller --> Biz_Processor
            Biz_Processor --> Math_Validator
            Biz_Processor --> OCR_Manager
        end

        subgraph "Secondary Adapters (Outbound)"
            DB_Repo[SQLAlchemy Repositories]
            Hermes_Gateway[Hermes Notification Client]
            
            Biz_Processor --> DB_Repo
            Biz_Processor --> Hermes_Gateway
        end
    end

    subgraph "External Systems"
        Postgres[(PostgreSQL Database)]
        Gemini[Gemini Vision API]
        Mail_Server[IMAP Mail Server]
        Hermes[Hermes MCP Server]

        API_Client --> REST
        Email_Poller -->|IMAPS 993| Mail_Server
        OCR_Manager -->|REST/HTTPS| Gemini
        DB_Repo -->|JDBC/SQL| Postgres
        Hermes_Gateway -->|MCP API| Hermes
    end
```

---

## 2. Thiết kế Cơ sở dữ liệu (Database Schema Design)

Để vừa đảm bảo tốc độ truy vấn báo cáo nhanh, vừa thích ứng linh hoạt với sự thay đổi của các hóa đơn chưa được chuẩn hóa, chúng tôi áp dụng mô hình **Hybrid Schema** (SQL Quan hệ + JSONB).

### 2.1 Bảng `invoices` (Thông tin đầu hóa đơn)
Lưu trữ các trường dữ liệu chung và quan trọng nhất của hóa đơn dùng cho tìm kiếm, thống kê:

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | `BIGSERIAL` | `PRIMARY KEY` | Định danh tự động tăng |
| `vendor` | `VARCHAR(255)` | `NOT NULL` | Tên nhà cung cấp |
| `tax_code` | `VARCHAR(50)` | `NULL` | Mã số thuế bên bán (nullable) |
| `invoice_number` | `VARCHAR(50)` | `NULL` | Số hóa đơn (nullable) |
| `invoice_date` | `DATE` | `NULL` | Ngày lập hóa đơn (YYYY-MM-DD) |
| `subtotal` | `NUMERIC(15, 2)` | `NOT NULL` | Tổng tiền trước thuế |
| `vat` | `NUMERIC(15, 2)` | `NOT NULL` | Tiền thuế GTGT |
| `total` | `NUMERIC(15, 2)` | `NOT NULL` | Tổng tiền thanh toán sau thuế |
| `file_path` | `VARCHAR(500)` | `NOT NULL` | Đường dẫn lưu file ảnh/PDF vật lý |
| `status` | `VARCHAR(50)` | `NOT NULL` | Trạng thái: `VALIDATED`, `WARNING`, `APPROVED` |
| `raw_payload` | `JSONB` | `NOT NULL` | Lưu cấu trúc JSON gốc trả về từ Gemini |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | Thời gian hệ thống thu thập |
| `updated_at` | `TIMESTAMP` | `DEFAULT NOW()` | Thời gian cập nhật cuối cùng |

*   **Chỉ mục (Index):**
    *   `idx_invoices_vendor` trên cột `vendor` (Bình thường hóa dạng index B-Tree để tìm kiếm tên cửa hàng).
    *   `idx_invoices_date` trên cột `invoice_date` (Tìm kiếm theo khoảng thời gian).
    *   `idx_invoices_raw_payload` dạng **GIN Index** trên cột `raw_payload` để cho phép truy vấn trực tiếp vào các thuộc tính JSON tùy biến.

### 2.2 Bảng `invoice_items` (Chi tiết dòng hàng)
Lưu trữ chi tiết từng sản phẩm/dịch vụ mua trong hóa đơn:

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | `BIGSERIAL` | `PRIMARY KEY` | Định danh tự động tăng |
| `invoice_id` | `BIGINT` | `FOREIGN KEY REFERENCES invoices(id) ON DELETE CASCADE` | Khóa ngoại liên kết hóa đơn |
| `name` | `VARCHAR(500)` | `NOT NULL` | Tên mặt hàng/dịch vụ |
| `quantity` | `NUMERIC(12, 4)` | `NOT NULL` | Số lượng (hỗ trợ số thập phân) |
| `unit_price` | `NUMERIC(15, 2)` | `NOT NULL` | Đơn giá sản phẩm |
| `total` | `NUMERIC(15, 2)` | `NOT NULL` | Thành tiền = Số lượng * Đơn giá |

### 2.3 Sơ đồ Quan hệ Thực thể (Entity Relationship Diagram - ERD)

```mermaid
erDiagram
    invoices {
        bigint id PK
        varchar vendor
        varchar tax_code
        varchar invoice_number
        date invoice_date
        numeric subtotal
        numeric vat
        numeric total
        varchar file_path
        varchar status
        jsonb raw_payload
        timestamp created_at
        timestamp updated_at
    }
    invoice_items {
        bigint id PK
        bigint invoice_id FK
        varchar name
        numeric quantity
        numeric unit_price
        numeric total
    }
    invoices ||--o{ invoice_items : "contains"
```

### 2.4 Sơ đồ Lớp SQLAlchemy (SQLAlchemy Class Diagram)

```mermaid
classDiagram
    class Invoice {
        +int id
        +str vendor
        +str tax_code
        +str invoice_number
        +date invoice_date
        +float subtotal
        +float vat
        +float total
        +str file_path
        +InvoiceStatus status
        +dict raw_payload
        +datetime created_at
        +datetime updated_at
        +List~InvoiceItem~ items
    }
    class InvoiceItem {
        +int id
        +Invoice invoice
        +str name
        +float quantity
        +float unit_price
        +float total
    }
    class InvoiceStatus {
        <<enumeration>>
        PROCESSING
        VALIDATED
        WARNING
        FAILED_EXTRACTION
        CORRUPTED_FILE
        APPROVED
    }
    Invoice "1" *-- "many" InvoiceItem : items
    Invoice --> InvoiceStatus : status
```

---

## 3. Luồng hoạt động tuần tự (Sequence Diagram)

Quy trình tự động hóa từ thu thập email đến kiểm đối dữ liệu trên web diễn ra tuần tự như sau:

```mermaid
sequenceDiagram
    autonumber
    actor Nhân viên
    actor Kế toán viên
    participant EM as Mail Server
    participant BK as Flask Backend
    participant GM as Gemini Vision API
    participant DB as PostgreSQL
    participant HS as Hermes MCP
    participant FE as Next.js Frontend

    Nhân viên->>EM: Gửi Email đính kèm ảnh hóa đơn
    loop Mỗi 5 phút (Email Polling)
        BK->>EM: Quét thư chưa đọc qua IMAPS
        EM-->>BK: Trả về thư đính kèm file ảnh/PDF
        BK->>BK: Tải file đính kèm, lưu file tạm
    end
    BK->>GM: Gửi file ảnh + Structured JSON Prompt
    GM-->>BK: Trả về dữ liệu JSON có cấu trúc
    BK->>BK: Thực hiện phép toán xác thực (Math Validation)
    BK->>DB: Lưu vào Database (Hybrid Schema - Trạng thái VALIDATED/WARNING)
    BK->>HS: Bắn thông báo (Telegram/Slack)
    HS-->>Nhân viên: Hiển thị thông báo kết quả trích xuất
    
    Kế toán viên->>FE: Mở trang Web Dashboard đối chiếu
    FE->>DB: Truy vấn danh sách hóa đơn
    DB-->>FE: Trả về danh sách
    Kế toán viên->>FE: Chọn hóa đơn cần kiểm tra (Side-by-Side View)
    FE->>BK: Yêu cầu file ảnh gốc & dữ liệu trích xuất
    BK-->>FE: Trả về dữ liệu
    Kế toán viên->>FE: Chỉnh sửa sai sót trên form (nếu có) & bấm Duyệt
    FE->>BK: Gửi dữ liệu phê duyệt cuối cùng
    BK->>DB: Cập nhật trạng thái thành APPROVED
    DB-->>FE: Phản hồi thành công
```

---

## 4. Đặc tả Cấu trúc Mã nguồn (Project Directory Structure)

Mã nguồn được tổ chức nhất quán để đảm bảo tính module hóa và dễ bảo trì:

```
ocr-invoice-engine/
├── .agent/                  # Cấu hình và Skill của AI Agent
├── apps/
│   ├── backend/             # Dự án Flask (Python 3.11/3.12)
│   │   ├── requirements.txt
│   │   ├── config.py        # Cấu hình Mail, Database, Gemini API
│   │   ├── wsgi.py          # Entrypoint WSGI
│   │   ├── app/
│   │   │   ├── __init__.py  # Cấu hình & khởi tạo Flask App & DB
│   │   │   ├── routes/      # REST API Blueprints (invoices.py)
│   │   │   ├── models/      # SQLAlchemy Models (invoice.py, invoice_item.py)
│   │   │   ├── services/    # Nghiệp vụ chính & Gemini Client
│   │   │   └── scheduler/   # APScheduler (IMAP Mail Poller)
│   │   └── tests/           # Unit / Integration Tests (pytest)
│   └── frontend/            # Dự án Next.js (TypeScript, React)
│       ├── package.json
│       └── src/
│           ├── components/  # Reusable UI Components
│           ├── pages/       # Next.js Pages (Dashboard, Reviewer)
│           └── styles/      # CSS files
├── docs/                    # Tài liệu Obsidian Vault theo chuẩn SOP-DEV-001
│   ├── 01-Requirements/     # SRS-001-ocr-invoice-system.md
│   ├── 02-Design/           # SAD-001-ocr-invoice-architecture.md
│   ├── 03-Specs/            # SPEC-002-ocr-invoice-design.md
│   └── 04-Development/      # PLAN-002, PLAN-04, task.md
└── .gitignore
```

---

## 5. Thiết kế Xử lý Ngoại lệ & Kỹ thuật Resilience (Exception & Resilience Design)

Để đảm bảo hệ thống chạy bền bỉ không bị sập giữa chừng, các thành phần kiến trúc xử lý lỗi được thiết kế như sau:

### 5.1 Exception Handling ở Backend (Flask)
- **`errorhandler` Blueprints:** Sử dụng `@app.errorhandler` toàn cục để bắt toàn bộ các lỗi runtime (ví dụ: `ValidationError`, `ResourceNotFound`, `GeminiAPIError`). Trả về mã lỗi HTTP chuẩn hóa kèm thông báo dạng JSON:
  ```json
  {
    "timestamp": "ISO-8601-Format",
    "status": 400,
    "error": "Bad Request",
    "message": "Chi tiết thông báo lỗi thân thiện",
    "code": "ERROR_CODE_SPECIFIC"
  }
  ```
- **IMAP Polling Resilience:** Trình quét mail chạy dưới dạng job của `APScheduler`. Khi phát sinh lỗi kết nối hoặc timeout IMAP:
  - Ghi nhận Error Log thông qua Python standard `logging`.
  - APScheduler sẽ tự động bỏ qua chu kỳ lỗi và tiếp tục thử lại ở chu kỳ tiếp theo sau 5 phút mà không làm sập tiến trình chính của ứng dụng Web.

- **Quản lý Trạng thái Hóa đơn (`InvoiceStatus` Enum):**
  - `PROCESSING`: File mới được Intake tải về, chưa gửi qua Gemini.
  - `VALIDATED`: Gemini phân tích thành công và vượt qua kiểm tra toán học.
  - `WARNING`: Gemini phân tích thành công nhưng sai lệch số liệu hoặc thiếu trường bắt buộc.
  - `FAILED_EXTRACTION`: Lỗi kết nối Gemini API, cho phép thử lại.
  - `CORRUPTED_FILE`: Tệp đính kèm bị lỗi định dạng hoặc không thể đọc được.
  - `APPROVED`: Kế toán viên đã đối chiếu và duyệt lưu trữ cuối cùng.

### 5.2 Xử lý lỗi ở Frontend (Next.js)
- **React Error Boundary:** Các trang Dashboard và View được bọc bởi Error Boundary. Nếu có lỗi render (ví dụ: file PDF lỗi gây sập viewer), ứng dụng chỉ render giao diện fallback thông báo lỗi cục bộ, không làm sập toàn bộ trang web.
- **Highlight Sai lệch Số liệu:** Khi nhận dữ liệu từ Backend có trạng thái `WARNING`, Next.js Frontend sẽ so sánh:
  - Nếu `sum(items.total) != subtotal`, tô viền đỏ trường `subtotal`.
- **Nút bấm Thử lại (Retry Action):** Nút bấm sẽ gọi API endpoint `/api/invoices/{id}/retry` để Backend thực hiện gửi lại file ảnh sang Gemini API, cập nhật trực tiếp dữ liệu trên màn hình mà không cần upload lại file thủ công.

---

## 6. Đặc tả Quy trình Email Intake (Python IMAP Polling Specification)

Hệ thống sử dụng thư viện `imaplib` và `email` tích hợp sẵn trong Python để thực hiện kết nối bảo mật IMAPS và quét các hóa đơn chưa đọc định kỳ:

```python
import imaplib
import email
from email.header import decode_header
import os

class EmailIntakeService:
    def __init__(self, imap_url, upload_dir):
        # imap_url format: imap.gmail.com
        self.imap_url = imap_url
        self.upload_dir = upload_dir

    def poll_unread_emails(self, username, password):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_url)
            mail.login(username, password)
            mail.select("inbox")

            # Chỉ tìm thư chưa đọc
            status, messages = mail.search(None, 'UNSEEN')
            if status != "OK":
                return []

            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822)')
                if status != "OK":
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Duyệt đính kèm
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename and (filename.endswith('.pdf') or filename.endswith('.png') or filename.endswith('.jpg')):
                        filepath = os.path.join(self.upload_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        # Sau đó lưu vào DB dưới trạng thái PROCESSING và gửi đi xử lý...
        except Exception as e:
            # Ghi log lỗi không để crash app
            print(f"Error in email polling: {e}")
```

- **Lưu ý triển khai:** Thông tin tài khoản hòm thư và thư mục lưu trữ được đọc từ file `.env` thông qua `os.getenv()`.

---

## 7. Đặc tả Prompt & Schema gửi Gemini Vision API (Gemini OCR Integration Specification)

Hệ thống gửi yêu cầu dạng REST HTTPS POST tới Gemini API sử dụng tính năng **Structured Outputs** để bắt buộc mô hình sinh ra dữ liệu có cấu trúc đúng định dạng JSON Schema.

### 7.1 Cấu trúc Request Payload
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Hãy đóng vai trò là một chuyên gia kế toán chuyên trích xuất hóa đơn tại Việt Nam. Hãy đọc hình ảnh hóa đơn đính kèm và trích xuất thông tin chính xác theo cấu trúc JSON Schema được yêu cầu. Đảm bảo đọc kỹ tên các mặt hàng (items), số lượng (quantity), đơn giá (unit_price), thành tiền (total = quantity * unit_price), tổng cộng tiền trước thuế (subtotal), thuế suất/tiền thuế (vat) và tổng tiền thanh toán (total). Nếu không có mã số thuế hoặc ký hiệu, hãy để null."
        },
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": "<BASE64_IMAGE_DATA>"
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_schema": {
      "type": "OBJECT",
      "properties": {
        "vendor": { "type": "STRING", "description": "Tên đơn vị bán lẻ/cửa hàng/công ty phát hành hóa đơn" },
        "tax_code": { "type": "STRING", "description": "Mã số thuế bên bán (nếu có, nếu không ghi null)", "nullable": true },
        "invoice_number": { "type": "STRING", "description": "Số hóa đơn hoặc số ký hiệu hóa đơn", "nullable": true },
        "date": { "type": "STRING", "description": "Ngày xuất hóa đơn dạng YYYY-MM-DD" },
        "subtotal": { "type": "NUMBER", "description": "Tổng cộng tiền hàng trước thuế" },
        "vat": { "type": "NUMBER", "description": "Tiền thuế GTGT" },
        "total": { "type": "NUMBER", "description": "Tổng tiền thanh toán cuối cùng bằng số" },
        "items": {
          "type": "ARRAY",
          "items": {
            "type": "OBJECT",
            "properties": {
              "name": { "type": "STRING", "description": "Tên hàng hóa hoặc dịch vụ" },
              "quantity": { "type": "NUMBER", "description": "Số lượng hàng hóa mua" },
              "unit_price": { "type": "NUMBER", "description": "Đơn giá của từng mặt hàng" },
              "total": { "type": "NUMBER", "description": "Thành tiền mặt hàng (bằng quantity * unit_price)" }
            },
            "required": ["name", "quantity", "unit_price", "total"]
          }
        }
      },
      "required": ["vendor", "date", "subtotal", "vat", "total", "items"]
    }
  }
}
```


