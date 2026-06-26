---
id: SPEC-002
title: OCR Invoice to JSON Processing Engine
status: approved
author: Antigravity
date: 2026-06-25
---

# SPEC-002: OCR Invoice to JSON Processing Engine

## Goal
Build an OCR engine that processes invoice images (VAT invoices, receipts, bills) and extracts structured JSON data using Gemini Vision API, wrapped in a Flask backend and presented with a Next.js frontend.

## Architecture

```
┌─────────────┐     POST /api/extract      ┌──────────────────┐     Gemini API      ┌─────────────┐
│   Next.js   │  ────────────────────────>  │     Flask        │  ────────────────>  │   Gemini    │
│  (Frontend) │  <────────────────────────  │   (Backend)      │  <────────────────  │  Vision API │
│             │     JSON response           │                  │     JSON result     │             │
└─────────────┘                             └──────────────────┘                     └─────────────┘
                                                    │
                                           ┌────────┴────────┐
                                           ▼                 ▼
                                    ┌──────────────┐  ┌──────────────┐
                                    │  PostgreSQL   │  │  MCP Servers │
                                    │  (Database)  │  │(Hermes/Stitch│
                                    └──────────────┘  └──────────────┘
```

### Components
1. **Frontend (Next.js)**:
   - Upload UI (drag-and-drop image files).
   - Side-by-side view showing the uploaded image and the extracted JSON values in an editable form.
   - History list to review previous extractions.
   - Code standards: **ESLint** & **Husky** pre-commit hooks.

2. **Backend (Flask)**:
   - Built with **Python 3.11/3.12**.
   - REST API endpoints for upload, extraction, and history.
   - Gemini Client: Integrates with Gemini 1.5 Flash/Pro using structured JSON output.
   - Database: **PostgreSQL** storing metadata, invoice file paths/storage refs, and extracted structured JSON data.
   - **MCP Bridge Clients**:
     - **Hermes MCP**: Send real-time notifications/messages to chat channels (e.g., Telegram, Slack) when an invoice is processed.
     - **Stitch MCP**: Align screen generation and visual design system templates.

3. **External Services**:
   - Google Gemini Vision API.

## Data Schema (Extracted JSON)
```json
{
  "vendor": "String (Name of vendor)",
  "tax_code": "String (Vendor tax code if present)",
  "invoice_number": "String (Invoice/receipt reference number)",
  "date": "String (YYYY-MM-DD)",
  "items": [
    {
      "name": "String",
      "quantity": "Number",
      "unit_price": "Number",
      "total": "Number"
    }
  ],
  "subtotal": "Number",
  "vat": "Number",
  "total": "Number"
}
```

## Security & Verification
- Verify input file size (< 10MB) and type (PNG, JPEG, PDF).
- Mathematical verification on backend: Sum(items.total) == subtotal; subtotal + vat == total.

## Database Design (Hybrid Schema)
We use a Hybrid Schema model in PostgreSQL to support structural queries while retaining maximum flexibility for varying invoice types:

1. **`invoices` Table (Common Header Fields)**
   - `id`: `SERIAL PRIMARY KEY`
   - `vendor`: `VARCHAR(255) NOT NULL` (Seller name)
   - `tax_code`: `VARCHAR(50)` (Vendor tax code, nullable for retail receipts)
   - `invoice_number`: `VARCHAR(50)` (Nullable)
   - `invoice_date`: `DATE` (Parsed date, YYYY-MM-DD)
   - `subtotal`: `NUMERIC(15, 2)` (Subtotal before tax)
   - `vat`: `NUMERIC(15, 2)` (Tax amount)
   - `total`: `NUMERIC(15, 2)` (Total amount)
   - `file_path`: `VARCHAR(500)` (Path to stored local/cloud image file)
   - `raw_payload`: `JSONB` (Stores the entire raw JSON returned by Gemini API for flexibility)

2. **`invoice_items` Table (Line Items)**
   - `id`: `SERIAL PRIMARY KEY`
   - `invoice_id`: `INTEGER REFERENCES invoices(id) ON DELETE CASCADE`
   - `name`: `VARCHAR(500) NOT NULL` (Product/service name)
   - `quantity`: `NUMERIC(12, 4)` (Support fractional quantities)
   - `unit_price`: `NUMERIC(15, 2)`
   - `total`: `NUMERIC(15, 2)` (Quantity * Unit Price)

