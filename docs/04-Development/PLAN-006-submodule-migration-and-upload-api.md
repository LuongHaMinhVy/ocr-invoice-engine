# PLAN-006: Submodule Alignment and Invoice Upload API Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Cleanly align the FastAPI backend files with the `apps/backend` Git Submodule, clean up parent repository tracking, and implement the core invoice upload, image streaming, and approval endpoints directly in the submodule.

**Architecture:** Copy backend scaffolding from the feature branch to the active backend submodule, stage and commit files in the submodule repo, and clean parent repo files to avoid conflicts. Implement the FastAPI routers for invoice upload (local storage + mock Gemini extraction), file streaming (FileResponse), and CRUD status management inside the submodule.

**Tech Stack:** Git Submodules, Python 3.11+, FastAPI, SQLAlchemy, pytest, python-multipart.

---

### Task 31: Backup and Migrate Backend Files to the Submodule

**Files:**
- Modify: `apps/backend` (Submodule directory in main workspace)

**Step 1: Write the failing test / check presence**
Verify that the `apps/backend` submodule directory currently only contains README.md and is clean.
Run:
```powershell
Get-ChildItem -Path apps/backend
```
Expected: Only `README.md` and `.git` exist in `apps/backend`.

**Step 2: Run verification command**
Run the check in powershell.

**Step 3: Write minimal implementation**
1. Copy all backend files from the worktree `.worktrees/ocr-invoice/apps/backend` to `apps/backend` in the main workspace:
```powershell
Copy-Item -Path .worktrees/ocr-invoice/apps/backend/* -Destination apps/backend/ -Recurse -Force
```
2. Navigate into `apps/backend`, check git status:
```powershell
cd apps/backend; git status
```
3. Stage and commit the backend scaffolding files *inside* the submodule directory:
```bash
git add .
git commit -m "feat: scaffold backend FastAPI project and database models"
```

**Step 4: Run test to verify it passes**
Run:
```powershell
git status
```
inside `apps/backend` to ensure the working directory is clean.

**Step 5: Commit**
*(This task commits directly inside the submodule, so we also push to submodule remote main if remote is set up).*
```bash
git push origin main
```

---

### Task 32: Clean up Parent Repository Backend Files

**Files:**
- Modify: parent repo `feature/ocr-invoice-impl` branch

**Step 1: Write the failing test / check presence**
Verify that parent git tracks normal backend files in `.worktrees/ocr-invoice/apps/backend`.
Run:
```powershell
git ls-files apps/backend
```
inside `.worktrees/ocr-invoice` to see tracked files.
Expected: Lists multiple files instead of just a submodule link.

**Step 2: Run verification command**
Run the check in powershell.

**Step 3: Write minimal implementation**
We need to remove the physical backend files from the parent branch and instead track only the submodule reference.
In the worktree `.worktrees/ocr-invoice`:
1. Remove tracked files in `apps/backend` while preserving the submodule gitlink:
```powershell
git rm -r --cached apps/backend
```
2. Clean up the physical directory if needed, and run `git submodule update --init` to restore the submodule pointer.
3. Add `apps/backend` submodule reference:
```powershell
git add apps/backend
```

**Step 4: Run test to verify it passes**
Run:
```powershell
git status
```
inside `.worktrees/ocr-invoice`.
Expected: Shows `apps/backend` submodule reference updated/modified, but no physical untracked backend files tracked by parent repo.

**Step 5: Commit**
```bash
git commit -m "chore: track apps/backend as submodule instead of regular files"
```

---

### Task 33: Setup Backend Virtual Environment and Dependencies

**Files:**
- Modify: `apps/backend/requirements.txt`

**Step 1: Write the failing test**
Try activating virtual environment or verifying dependencies in `apps/backend`.
Run:
```powershell
cd apps/backend; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt
```
Expected: Standard dependency installation.

**Step 2: Run verification command**
Run the command in powershell.

**Step 3: Write minimal implementation**
If any dependencies (like `python-multipart`, `pytest`, `black`, `flake8`) are missing from `requirements.txt`, append them:
```txt
python-multipart>=0.0.9
pytest>=8.0.0
black>=24.0.0
flake8>=7.0.0
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest --version
```
inside active virtualenv.
Expected: Output shows pytest version.

**Step 5: Commit**
Commit inside `apps/backend` submodule:
```bash
git add requirements.txt
git commit -m "chore: add upload and testing dependencies to requirements.txt"
```

---

### Task 34: Implement Invoice Upload API & Local Storage

**Files:**
- Create: `apps/backend/app/routers/invoices.py`
- Create: `apps/backend/tests/test_upload.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_upload.py` in the submodule asserting the upload behavior:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_invoice_endpoint_not_found():
    response = client.post("/api/invoices/upload")
    # Endpoint is not implemented yet
    assert response.status_code == 404
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest tests/test_upload.py -v
```
Expected: FAIL (or 404/405).

**Step 3: Write minimal implementation**
1. Implement the router `apps/backend/app/routers/invoices.py`:
```python
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.invoice_status import InvoiceStatus

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=201)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ["image/png", "image/jpeg", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Simulated Gemini extraction & math validation
    vendor = "Extracted Vendor"
    subtotal, vat, total = 100.0, 10.0, 110.0
    status_val = InvoiceStatus.VALIDATED
    
    invoice = Invoice(
        vendor=vendor,
        subtotal=subtotal,
        vat=vat,
        total=total,
        file_path=file_path,
        status=status_val
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    item = InvoiceItem(invoice_id=invoice.id, name="Extracted Item", quantity=1.0, unit_price=100.0, total=100.0)
    db.add(item)
    db.commit()
    
    return {
        "id": invoice.id,
        "vendor": invoice.vendor,
        "total": invoice.total,
        "status": invoice.status.value
    }
```
2. Include the router in `apps/backend/app/routers/__init__.py` or `apps/backend/main.py`:
```python
from app.routers import invoices
app.include_router(invoices.router)
```

**Step 4: Run test to verify it passes**
Update `tests/test_upload.py` to assert success:
```python
def test_upload_invoice_success():
    file_data = {"file": ("test_invoice.png", b"fake_image_bytes", "image/png")}
    response = client.post("/api/invoices/upload", files=file_data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["vendor"] == "Extracted Vendor"
    assert json_data["total"] == 110.0
```
Run:
```powershell
pytest tests/test_upload.py -v
```
Expected: PASS

**Step 5: Commit**
Commit inside the backend submodule:
```bash
git add app/routers/invoices.py app/main.py tests/test_upload.py
git commit -m "feat: implement file upload API with local storage"
```

---

### Task 35: Implement Image Streaming and CRUD Approval

**Files:**
- Modify: `apps/backend/app/routers/invoices.py`
- Create: `apps/backend/tests/test_crud.py`

**Step 1: Write the failing test**
Create `apps/backend/tests/test_crud.py` asserting CRUD endpoints:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_stream_invoice_image_not_found():
    response = client.get("/api/invoices/9999/image")
    assert response.status_code == 404
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest tests/test_crud.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**
Implement image streaming and manual approval in `apps/backend/app/routers/invoices.py`:
```python
from fastapi.responses import FileResponse

@router.get("")
def list_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()

@router.get("/{invoice_id}/image")
def get_invoice_image(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice or not invoice.file_path or not os.path.exists(invoice.file_path):
        raise HTTPException(status_code=404, detail="Invoice image not found")
    return FileResponse(invoice.file_path)

@router.post("/{invoice_id}/approve")
def approve_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = InvoiceStatus.APPROVED
    db.commit()
    return {"status": "success", "invoice_status": invoice.status.value}
```

**Step 4: Run test to verify it passes**
Update `tests/test_crud.py` and run:
```powershell
pytest tests/test_crud.py -v
```
Expected: PASS

**Step 5: Commit**
Commit inside the backend submodule:
```bash
git add app/routers/invoices.py tests/test_crud.py
git commit -m "feat: implement image streaming and manual approval endpoints"
```
