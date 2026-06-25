---
id: SPEC-002
title: OCR Invoice to JSON Processing Engine
status: approved
author: Antigravity
date: 2026-06-25
---

# SPEC-002: OCR Invoice to JSON Processing Engine

## Goal
Build an OCR engine that processes invoice images (VAT invoices, receipts, bills) and extracts structured JSON data using Gemini Vision API, wrapped in a Spring Boot backend and presented with a Next.js frontend.

## Architecture

```
┌─────────────┐     POST /api/extract      ┌──────────────────┐     Gemini API      ┌─────────────┐
│   Next.js   │  ────────────────────────>  │   Spring Boot    │  ────────────────>  │   Gemini    │
│  (Frontend) │  <────────────────────────  │   (Backend)      │  <────────────────  │  Vision API │
│             │     JSON response           │                  │     JSON result     │             │
└─────────────┘                             └──────────────────┘                     └─────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │  PostgreSQL   │
                                            │  (History)    │
                                            └──────────────┘
```

### Components
1. **Frontend (Next.js)**:
   - Upload UI (drag-and-drop image files).
   - Side-by-side view showing the uploaded image and the extracted JSON values in an editable form.
   - History list to review previous extractions.
   - Export feature (JSON, Excel).

2. **Backend (Spring Boot)**:
   - REST API endpoints for upload, extraction, and history management.
   - Gemini Client: Integrates with Gemini 1.5 Flash/Pro using structured JSON output schemas.
   - Database: PostgreSQL storing metadata, invoice file paths/storage refs, and extracted structured JSON data.

3. **External Services**:
   - Google Gemini Vision API: Used to perform multi-modal extraction directly from image files.

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
- Database storage of original image and JSON data for audit trail.
