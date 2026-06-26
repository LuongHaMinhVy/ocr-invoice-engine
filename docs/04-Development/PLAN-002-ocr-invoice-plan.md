# OCR Invoice Processing Monorepo Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build a monorepo containing a Python FastAPI backend (SQLAlchemy, PostgreSQL, pytest, Uvicorn) and a Next.js frontend (ESLint, Husky) that extracts structured JSON from invoice images using Gemini Vision API, with notifications routed to Hermes MCP and UI styling synchronized with Stitch MCP.

**Architecture:** A Next.js frontend allows users to upload invoice images, which are sent via REST to a FastAPI backend. The backend forwards the image to the Gemini Vision API using a structured schema (Pydantic), validates calculations, stores the output in PostgreSQL, triggers a Hermes notification message, and returns the JSON to the client.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic, psycopg2-binary, pytest, httpx, Next.js 14.2.x / 15.x (App Router), TypeScript, ESLint, Husky, Gemini API, Hermes MCP REST client, Stitch MCP.

---

### Task 1: Project Scaffolding and Routing

**Files:**
- Create: `apps/backend/requirements.txt`
- Create: `apps/backend/config.py`
- Create: `apps/backend/main.py`
- Create: `apps/backend/app/__init__.py`
- Create: `apps/backend/app/database.py`
- Create: `apps/backend/app/routers/__init__.py`
- Create: `apps/backend/app/routers/invoices.py`
- Test: `apps/backend/tests/test_routes.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_routes.py` to verify that FastAPI app initializes and responds to the health check endpoint:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/invoices/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_routes.py -v
```
Expected: FAIL (ModuleNotFoundError: No module named 'main' or pytest command fails).

**Step 3: Write minimal implementation**
1. Create `apps/backend/requirements.txt`:
```
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.4
sqlalchemy==2.0.31
psycopg2-binary==2.9.9
pytest==8.2.2
httpx==0.27.0
google-generativeai==0.5.4
requests==2.32.3
apscheduler==3.10.4
python-dotenv==1.0.1
```

2. Create `apps/backend/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ocr_invoice")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
```

3. Create `apps/backend/app/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

4. Create `apps/backend/app/routers/invoices.py`:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

@router.get("/health")
def health_check():
    return {"status": "OK"}
```

5. Create `apps/backend/app/__init__.py`:
```python
# Marker file to make app a package
```

6. Create `apps/backend/main.py`:
```python
from fastapi import FastAPI
from app.routers.invoices import router as invoices_router
from app.database import engine, Base

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OCR Invoice Processing API")

app.include_router(invoices_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pip install -r apps/backend/requirements.txt
pytest apps/backend/tests/test_routes.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/requirements.txt apps/backend/config.py apps/backend/main.py apps/backend/app/ apps/backend/tests/
git commit -m "feat: scaffold FastAPI backend with health check endpoint"
```

---

### Task 2: Configure PostgreSQL Database & Entity Models

**Files:**
- Create: `apps/backend/app/models/invoice_status.py`
- Create: `apps/backend/app/models/invoice.py`
- Create: `apps/backend/app/models/invoice_item.py`
- Test: `apps/backend/tests/test_models.py`

**Step 1: Write a failing database model test**
Create `apps/backend/tests/test_models.py` testing invoice saving:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.invoice import Invoice
from app.models.invoice_status import InvoiceStatus

@pytest.fixture
def db_session():
    # Use SQLite memory for testing models
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_save_invoice(db_session):
    invoice = Invoice(
        vendor="Test Vendor",
        total=150000.0,
        status=InvoiceStatus.PROCESSING
    )
    db_session.add(invoice)
    db_session.commit()
    assert invoice.id is not None
    assert invoice.status == InvoiceStatus.PROCESSING
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_models.py -v
```
Expected: FAIL (Compilation/Import error - missing model classes).

**Step 3: Write minimal implementation**
1. Create `apps/backend/app/models/invoice_status.py`:
```python
import enum

class InvoiceStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    VALIDATED = "VALIDATED"
    WARNING = "WARNING"
    FAILED_EXTRACTION = "FAILED_EXTRACTION"
    CORRUPTED_FILE = "CORRUPTED_FILE"
    APPROVED = "APPROVED"
```

2. Create `apps/backend/app/models/invoice.py`:
```python
from sqlalchemy import Column, BigInteger, String, Date, Float, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.invoice_status import InvoiceStatus

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vendor = Column(String(255), nullable=False)
    tax_code = Column(String(50), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    invoice_date = Column(Date, nullable=True)
    subtotal = Column(Float, nullable=True)
    vat = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    file_path = Column(String(500), nullable=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PROCESSING, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
```

3. Create `apps/backend/app/models/invoice_item.py`:
```python
from sqlalchemy import Column, BigInteger, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id = Column(BigInteger, ForeignKey("invoices.id"), nullable=False)
    name = Column(String(500), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
```

4. Make sure models are registered by updating `apps/backend/app/models/__init__.py`:
```python
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.invoice_status import InvoiceStatus
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest apps/backend/tests/test_models.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/app/models/ apps/backend/tests/test_models.py
git commit -m "feat: configure postgresql SQLAlchemy entities and status enums for FastAPI"
```

---

### Task 3: Initialize Next.js Frontend with ESLint & Husky

**Files:**
- Create: `apps/frontend/package.json`
- Create: `apps/frontend/.eslintrc.json`
- Create: `apps/frontend/.husky/pre-commit`
- Create: `apps/frontend/src/app/page.tsx`

**Step 1: Write a failing validation check**
Verify ESLint config exists and runs:
Run: `npm --prefix frontend run lint`
Expected: FAIL (missing eslint configuration or dependency packages).

**Step 2: Scaffold Next.js project with ESLint & Husky**
1. Initialize frontend package.json, configure Tailwind and standard directory structures.
2. Configure pre-commit husky hooks running ESLint.

**Step 3: Run validation to verify it passes**
Run: `npm --prefix frontend run lint`
Expected: PASS (zero lint errors).

**Step 4: Commit**
```bash
git add apps/frontend/
git commit -m "feat: initialize next.js frontend with eslint and husky hook"
```

---

### Task 4: Implement Gemini API Client and Math Verification

**Files:**
- Create: `apps/backend/app/schemas/invoice.py`
- Create: `apps/backend/app/services/gemini_service.py`
- Test: `apps/backend/tests/test_gemini_service.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_gemini_service.py` that mocks the Gemini API response and validates math equations.
Run:
```powershell
pytest apps/backend/tests/test_gemini_service.py -v
```
Expected: FAIL (missing service/module).

**Step 2: Implement Pydantic Schema and GeminiClient**
1. Create `apps/backend/app/schemas/invoice.py` to define Gemini Structured Output target:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class InvoiceItemSchema(BaseModel):
    name: str = Field(description="Tên hàng hóa hoặc dịch vụ")
    quantity: float = Field(description="Số lượng hàng hóa")
    unit_price: float = Field(description="Đơn giá của mặt hàng")
    total: float = Field(description="Thành tiền (bằng quantity * unit_price)")

class InvoiceExtractionSchema(BaseModel):
    vendor: str = Field(description="Tên đơn vị bán lẻ/cửa hàng/công ty phát hành hóa đơn")
    tax_code: Optional[str] = Field(None, description="Mã số thuế bên bán")
    invoice_number: Optional[str] = Field(None, description="Số hóa đơn hoặc số ký hiệu hóa đơn")
    date: str = Field(description="Ngày xuất hóa đơn dạng YYYY-MM-DD")
    subtotal: float = Field(description="Tổng cộng tiền hàng trước thuế")
    vat: float = Field(description="Tiền thuế GTGT")
    total: float = Field(description="Tổng tiền thanh toán cuối cùng")
    items: List[InvoiceItemSchema] = Field(description="Danh sách các mặt hàng chi tiết")
```

2. Create `apps/backend/app/services/gemini_service.py`:
```python
import google.generativeai as genai
import json
from app.schemas.invoice import InvoiceExtractionSchema

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_invoice(self, image_bytes: bytes, mime_type: str) -> dict:
        # Implementation calling Gemini structured output with schema
        # returns parsed dictionary matching InvoiceExtractionSchema
        pass

    def validate_invoice_math(self, data: dict) -> str:
        subtotal = data.get("subtotal", 0.0)
        vat = data.get("vat", 0.0)
        total = data.get("total", 0.0)
        items = data.get("items", [])
        
        sum_items = sum(item.get("total", 0.0) for item in items)
        
        # Accept small float delta
        math_ok = abs(sum_items - subtotal) < 0.01 and abs(subtotal + vat - total) < 0.01
        return "VALIDATED" if math_ok else "WARNING"
```

**Step 3: Run test to verify passes**
Run:
```powershell
pytest apps/backend/tests/test_gemini_service.py -v
```
Expected: PASS

**Step 4: Commit**
```bash
git add apps/backend/app/schemas/ apps/backend/app/services/gemini_service.py apps/backend/tests/test_gemini_service.py
git commit -m "feat: implement gemini client and backend math validation using Pydantic schemas"
```

---

### Task 5: Implement Next.js OCR Upload and History View Interface

**Files:**
- Modify: `apps/frontend/src/app/page.tsx`
- Create: `apps/frontend/src/components/InvoiceList.tsx`
- Create: `apps/frontend/src/components/SideBySideView.tsx`

**Step 1: Write a failing layout test**
Verify layout renders main upload panel.
Run: `npm --prefix frontend run test` (if unit test configured) or run build.
Expected: FAIL.

**Step 2: Implement side-by-side editing view**
Build components using dynamic CSS design aesthetics. Keep styling sleek, minimalist dark/light mode adaptable.

**Step 3: Verify build passes**
Run: `npm --prefix frontend run build`
Expected: SUCCESS.

**Step 4: Commit**
```bash
git add apps/frontend/src/
git commit -m "feat: implement main OCR upload dashboard and side-by-side editing interface"
```
