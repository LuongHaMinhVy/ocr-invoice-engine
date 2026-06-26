# OCR Invoice Processing Monorepo Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Build a monorepo containing a Python Flask backend (SQLAlchemy, PostgreSQL, pytest) and a Next.js frontend (ESLint, Husky) that extracts structured JSON from invoice images using Gemini Vision API, with notifications routed to Hermes MCP and UI styling synchronized with Stitch MCP.

**Architecture:** A Next.js frontend allows users to upload invoice images, which are sent via REST to a Flask backend. The backend forwards the image to the Gemini Vision API using a structured schema, validates calculations, stores the output in PostgreSQL, triggers a Hermes notification message, and returns the JSON to the client.

**Tech Stack:** Python 3.11+, Flask, Flask-SQLAlchemy, psycopg2-binary, pytest, Next.js 14.2.x / 15.x (App Router), TypeScript, ESLint, Husky, Gemini API, Hermes MCP REST client, Stitch MCP.

---

### Task 1: Project Scaffolding and Routing

**Files:**
- Create: `apps/backend/requirements.txt`
- Create: `apps/backend/config.py`
- Create: `apps/backend/wsgi.py`
- Create: `apps/backend/app/__init__.py`
- Create: `apps/backend/app/routes/__init__.py`
- Create: `apps/backend/app/routes/invoices.py`
- Test: `apps/backend/tests/test_routes.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_routes.py` to verify that Flask app initializes and responds to the health check endpoint:
```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/api/invoices/health")
    assert response.status_code == 200
    assert response.json == {"status": "OK"}
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_routes.py -v
```
Expected: FAIL (ModuleNotFoundError: No module named 'app' or pytest command fails).

**Step 3: Write minimal implementation**
1. Create `apps/backend/requirements.txt`:
```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
pytest==8.2.2
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

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ocr_invoice")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

3. Create `apps/backend/app/__init__.py`:
```python
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.invoices import invoices_bp
    app.register_blueprint(invoices_bp, url_prefix="/api/invoices")

    return app
```

4. Create `apps/backend/app/routes/invoices.py`:
```python
from flask import Blueprint, jsonify

invoices_bp = Blueprint("invoices", __name__)

@invoices_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200
```

5. Create `apps/backend/wsgi.py`:
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
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
git add apps/backend/requirements.txt apps/backend/config.py apps/backend/wsgi.py apps/backend/app/ apps/backend/tests/
git commit -m "feat: scaffold Flask backend with health check endpoint"
```

---

### Task 2: Configure PostgreSQL Database & Entity Models

**Files:**
- Create: `apps/backend/app/models/invoice_status.py`
- Create: `apps/backend/app/models/invoice.py`
- Create: `apps/backend/app/models/invoice_item.py`
- Modify: `apps/backend/app/__init__.py`
- Test: `apps/backend/tests/test_models.py`

**Step 1: Write a failing database model test**
Create `apps/backend/tests/test_models.py` testing invoice saving:
```python
import pytest
from app import create_app, db
from app.models.invoice import Invoice
from app.models.invoice_status import InvoiceStatus

@pytest.fixture
def client_db():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_save_invoice(client_db):
    invoice = Invoice(
        vendor="Test Vendor",
        total=150000.0,
        status=InvoiceStatus.PROCESSING
    )
    client_db.session.add(invoice)
    client_db.session.commit()
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
1. Modify `apps/backend/app/__init__.py` to initialize SQLAlchemy:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes.invoices import invoices_bp
    app.register_blueprint(invoices_bp, url_prefix="/api/invoices")

    return app
```

2. Create `apps/backend/app/models/invoice_status.py`:
```python
import enum

class InvoiceStatus(enum.Enum):
    PROCESSING = "PROCESSING"
    VALIDATED = "VALIDATED"
    WARNING = "WARNING"
    FAILED_EXTRACTION = "FAILED_EXTRACTION"
    CORRUPTED_FILE = "CORRUPTED_FILE"
    APPROVED = "APPROVED"
```

3. Create `apps/backend/app/models/invoice.py`:
```python
from app import db
from datetime import datetime
from app.models.invoice_status import InvoiceStatus

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    vendor = db.Column(db.String(255), nullable=False)
    tax_code = db.Column(db.String(50), nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    invoice_date = db.Column(db.Date, nullable=True)
    subtotal = db.Column(db.Float, nullable=True)
    vat = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Enum(InvoiceStatus), default=InvoiceStatus.PROCESSING, nullable=False)
    raw_payload = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("InvoiceItem", backref="invoice", cascade="all, delete-orphan")
```

4. Create `apps/backend/app/models/invoice_item.py`:
```python
from app import db

class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.BigInteger, db.ForeignKey("invoices.id"), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest apps/backend/tests/test_models.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/app/__init__.py apps/backend/app/models/ apps/backend/tests/test_models.py
git commit -m "feat: configure postgresql SQLAlchemy entities and status enums"
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
Use npm or npx setups:
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
- Create: `apps/backend/app/services/gemini_service.py`
- Test: `apps/backend/tests/test_gemini_service.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_gemini_service.py` that mocks the Gemini API response and validates math equations.
Run:
```powershell
pytest apps/backend/tests/test_gemini_service.py -v
```
Expected: FAIL (missing service/module).

**Step 2: Implement GeminiClient and Validator**
Create `apps/backend/app/services/gemini_service.py`:
```python
import google.generativeai as genai
import json

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_invoice(self, image_bytes, mime_type):
        # Implementation calling Gemini structured output
        # Returns parsed JSON dict
        pass

    def validate_invoice_math(self, data):
        # returns status, log_messages
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
git add apps/backend/app/services/gemini_service.py apps/backend/tests/test_gemini_service.py
git commit -m "feat: implement gemini client and backend math validation service"
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
