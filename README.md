# E-Invoice OCR & Verification Engine (FastAPI + Next.js)

Hệ thống tự động hóa Thu thập và Đối chiếu Hóa đơn (Automated Invoice Intake & Verification Pipeline) giúp giảm thiểu quy trình nhập liệu thủ công, tự động quét hòm thư, trích xuất dữ liệu hóa đơn thông qua AI (Gemini Vision API) và kiểm đối số liệu trước khi duyệt lưu trữ.

---

## 1. Kiến trúc & Sơ đồ luồng (Architecture & Flow)

Hệ thống hoạt động theo mô hình Monorepo kết hợp giao tiếp API REST:

```
┌─────────────┐     POST /api/invoices     ┌──────────────────┐     Gemini API      ┌─────────────┐
│   Next.js   │  ────────────────────────>  │    FastAPI       │  ────────────────  │   Gemini    │
│  (Frontend) │  <────────────────────────  │   (Backend)      │  <────────────────  │  Vision API │
│   Port 3000 │     JSON Response           │   Port 8000      │     JSON Result     │  (Pydantic) │
└─────────────┘                             └────────┬─────────┘                     └─────────────┘
                                                     │
                                            ┌────────┴────────┐
                                            ▼                 ▼
                                     ┌──────────────┐  ┌──────────────┐
                                     │  PostgreSQL   │  │  MCP Servers │
                                     │  (Database)  │  │(Hermes/Stitch│
                                     └──────────────┘  └──────────────┘
```

1. **Email Intake (APScheduler & IMAP):** Định kỳ quét hòm thư để tải tệp hóa đơn đính kèm (PNG, JPEG, PDF) lưu vào bộ nhớ tạm.
2. **OCR & Analytics (Gemini API):** Trích xuất thông tin hóa đơn dưới cấu trúc JSON chuẩn hóa (Pydantic Schema).
3. **Validation & Matching Engine:** Đối chiếu các biểu thức toán học (Tổng dòng hàng == Subtotal; Subtotal + VAT == Total) để đưa ra cảnh báo nếu có chênh lệch.
4. **Hermes MCP Gateway:** Tự động bắn thông báo tình trạng hóa đơn thời gian thực tới các kênh liên lạc (Telegram, Slack).
5. **Next.js Interface:** Giao diện cho phép tải trực tiếp file hóa đơn lên, xem danh sách lịch sử và đối chiếu side-by-side trước khi phê duyệt.

---

## 2. Cấu trúc mã nguồn (Monorepo Directory Structure)

```
ocr-invoice-engine/
├── .agent/                  # Cấu hình và Skill của AI Agent
├── apps/
│   ├── backend/             # FastAPI Backend (Python 3.11+)
│   │   ├── app/
│   │   │   ├── database.py  # Cấu hình kết nối DB engine
│   │   │   ├── routers/     # API Route (health, invoices)
│   │   │   ├── models/      # SQLAlchemy Models (Invoice, InvoiceItem)
│   │   │   ├── schemas/     # Pydantic Schemas validate dữ liệu
│   │   │   ├── services/    # Gemini OCR Client, Mail Poller & Hermes Service
│   │   │   └── scheduler/   # APScheduler quản lý job chạy nền
│   │   ├── tests/           # Kịch bản kiểm thử TDD (pytest)
│   │   └── requirements.txt
│   └── frontend/            # Next.js Frontend (React, TypeScript)
│       └── src/             # Giao diện & components đối chiếu hóa đơn
├── docs/                    # Tài liệu đặc tả hệ thống & Thiết kế kiến trúc
└── README.md
```

---

## 3. Cấu hình hệ thống (Configuration)

Tạo tệp `.env` tại thư mục gốc hoặc cụ thể trong `apps/backend/` và cấu hình các thông số sau:

```env
# Database Connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/ocr_invoice

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key

# Hermes MCP Notification Bridge
HERMES_BRIDGE_URL=http://localhost:8089
HERMES_NOTIFICATION_TARGET=telegram:-1002148765432

# Email IMAP Settings
IMAP_SERVER=imap.gmail.com
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=your_app_specific_password
```

---

## 4. Hướng dẫn khởi chạy (Getting Started)

### 4.1 Khởi chạy Backend (FastAPI)
1. Di chuyển tới thư mục backend:
   ```bash
   cd apps/backend
   ```
2. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv venv
   # Trên Windows:
   .\venv\Scripts\activate
   # Trên macOS/Linux:
   source venv/bin/activate
   ```
3. Cài đặt các gói phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
4. Chạy ứng dụng thông qua Uvicorn:
   ```bash
   python main.py
   ```
   API sẽ hoạt động tại địa chỉ: `http://localhost:8000`  
   Tài liệu Swagger API tự động tại: `http://localhost:8000/docs`

### 4.2 Khởi chạy Frontend (Next.js)
*Lưu ý: Dự án sử dụng trình quản lý gói `pnpm`.*
1. Di chuyển tới thư mục frontend:
   ```bash
   cd apps/frontend
   ```
2. Cài đặt các thư viện:
   ```bash
   pnpm install
   ```
3. Khởi chạy dev server:
   ```bash
   pnpm dev
   ```
   Giao diện hoạt động tại địa chỉ: `http://localhost:3000`

---

## 5. Kiểm thử hệ thống (Running Tests)

Hệ thống được phát triển theo mô hình kiểm thử hướng phát triển (**TDD**). Toàn bộ các testcase backend nằm trong thư mục `apps/backend/tests/`.

Chạy bộ kiểm thử bằng lệnh:
```bash
cd apps/backend
pytest -v
```

---

## 6. Hướng dẫn vận hành MCP (Model Context Protocol)

Khi làm việc với các AI Agent lập trình trong không gian làm việc này:
* **PostgreSQL MCP:** Cấu hình plugin kết nối thẳng vào database của bạn để cho phép Agent kiểm tra schema của bảng hóa đơn mà không cần truy vấn terminal thô.
* **Hermes MCP:** Hãy chắc chắn khởi chạy REST bridge của Hermes tại port `8089` trước khi kiểm thử tính năng gửi tin nhắn/cảnh báo hóa đơn.
* **Stitch MCP:** Dùng để áp dụng thiết kế UI và quản lý layout đồng nhất.
