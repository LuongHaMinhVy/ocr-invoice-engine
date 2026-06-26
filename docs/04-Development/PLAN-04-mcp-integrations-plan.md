# Email Intake & PostgreSQL MCP Integrations Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implement automated invoice intake by polling email attachments via Python IMAP (using APScheduler) and set up PostgreSQL MCP server for database validation.

**Architecture:** Initialize APScheduler inside the FastAPI lifespan context manager to start and stop the scheduler automatically. Schedule an EmailIntakeService that connects via IMAP to poll unread emails for image/PDF attachments, saves them to temporary storage, and routes them to the OCR engine. Configure Postgres MCP server in settings.

**Tech Stack:** Python 3.11+, FastAPI, APScheduler, imaplib, email, PostgreSQL MCP, requests.

---

### Task 1: Add Email Polling Dependencies

**Files:**
- Modify: `apps/backend/requirements.txt`

**Step 1: Write the failing test / check dependency presence**
Verify that `apscheduler` package is not yet in requirements.txt.
Run:
```powershell
Select-String -Path apps/backend/requirements.txt -Pattern "apscheduler"
```
Expected: Pattern not found / blank output.

**Step 2: Add dependencies to requirements.txt**
Verify `apscheduler` is listed in requirements.txt (added in Task 1 of PLAN-002). If not, append it.

**Step 3: Run pip install to verify dependencies compile successfully**
Run:
```powershell
pip install -r apps/backend/requirements.txt
```
Expected: SUCCESS

**Step 4: Commit**
```bash
git add apps/backend/requirements.txt
git commit -m "feat: add FastAPI backend APScheduler dependencies"
```

---

### Task 2: Implement Mail Polling Scheduler Configuration

**Files:**
- Create: `apps/backend/app/scheduler/__init__.py`
- Create: `apps/backend/app/scheduler/jobs.py`
- Modify: `apps/backend/main.py`
- Test: `apps/backend/tests/test_scheduler.py`

**Step 1: Write the failing test**
Create a scheduler test file `apps/backend/tests/test_scheduler.py` that asserts the APScheduler is configured and has our email polling job registered.
Run:
```powershell
pytest apps/backend/tests/test_scheduler.py -v
```
Expected: FAIL due to missing scheduler modules.

**Step 2: Implement scheduler setup**
1. Create `apps/backend/app/scheduler/jobs.py`:
```python
def email_polling_job():
    # Job execution placeholder
    pass
```

2. Create `apps/backend/app/scheduler/__init__.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.jobs import email_polling_job

def init_scheduler():
    scheduler = BackgroundScheduler()
    # Poll every 5 minutes
    scheduler.add_job(email_polling_job, 'interval', minutes=5, id='email_poll_job')
    scheduler.start()
    return scheduler

def shutdown_scheduler(scheduler):
    if scheduler and scheduler.running:
        scheduler.shutdown()
```

3. Modify `apps/backend/main.py` to register the scheduler inside a lifespan context manager:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.invoices import router as invoices_router
from app.database import engine, Base
from app.scheduler import init_scheduler, shutdown_scheduler

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip scheduler in testing/reload if needed, or run once
    scheduler = init_scheduler()
    yield
    shutdown_scheduler(scheduler)

app = FastAPI(title="OCR Invoice Processing API", lifespan=lifespan)

app.include_router(invoices_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
```

**Step 3: Run test to verify passes**
Run:
```powershell
pytest apps/backend/tests/test_scheduler.py -v
```
Expected: PASS

**Step 4: Commit**
```bash
git add apps/backend/app/scheduler/ apps/backend/main.py apps/backend/tests/test_scheduler.py
git commit -m "feat: configure background APScheduler for email polling in FastAPI lifespan"
```

---

### Task 3: Implement EmailIntakeService and Attachment Extraction

**Files:**
- Create: `apps/backend/app/services/email_intake_service.py`
- Test: `apps/backend/tests/test_email_intake.py`

**Step 1: Write failing test**
Create a test that mocks `imaplib.IMAP4_SSL` returning a multipart email containing a PDF attachment, and verifies that `EmailIntakeService.extract_attachments()` extracts it successfully.
Run:
```powershell
pytest apps/backend/tests/test_email_intake.py -v
```
Expected: FAIL

**Step 2: Implement EmailIntakeService**
Implement email fetching and file extraction:
```python
import os
import imaplib
import email

class EmailIntakeService:
    def __init__(self, upload_dir):
        self.upload_dir = upload_dir

    def extract_attachments(self, msg):
        files = []
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
                files.append(filepath)
        return files
```

**Step 3: Run test**
Run:
```powershell
pytest apps/backend/tests/test_email_intake.py -v
```
Expected: PASS

**Step 4: Commit**
```bash
git add apps/backend/app/services/email_intake_service.py apps/backend/tests/test_email_intake.py
git commit -m "feat: implement email intake attachment extraction service"
```

---

### Task 4: Implement Hermes MCP Notification Client

**Files:**
- Create: `apps/backend/app/services/hermes_service.py`
- Test: `apps/backend/tests/test_hermes_service.py`

**Step 1: Write failing test**
Create a test file `apps/backend/tests/test_hermes_service.py` to assert that `HermesService.send_invoice_notification` calls the correct bridge URL with the correct payload:
```python
import pytest
from unittest.mock import patch
from app.services.hermes_service import HermesService

@patch("requests.post")
def test_send_notification(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}

    service = HermesService(bridge_url="http://localhost:8089", target="telegram:-1002148765432")
    success = service.send_invoice_notification(invoice_id=1, vendor="Cửa hàng tiện lợi", total=50000.0, status="VALIDATED")
    
    assert success is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["target"] == "telegram:-1002148765432"
    assert "Cửa hàng tiện lợi" in kwargs["json"]["message"]
```

**Step 2: Implement HermesService**
Create `apps/backend/app/services/hermes_service.py`:
```python
import requests
import logging

logger = logging.getLogger(__name__)

class HermesService:
    def __init__(self, bridge_url, target):
        self.bridge_url = bridge_url
        self.target = target

    def send_invoice_notification(self, invoice_id, vendor, total, status):
        if not self.bridge_url or not self.target:
            logger.warning("Hermes configuration missing. Skipping notification.")
            return False

        message = (
            f"🔔 [OCR Invoice] Phát hiện hóa đơn mới!\n"
            f"- Nhà cung cấp: {vendor}\n"
            f"- Tổng tiền: {total:,.2f} VNĐ\n"
            f"- Trạng thái xác thực: {status}\n"
            f"- Link đối chiếu: http://localhost:3000/invoices/{invoice_id}"
        )

        try:
            response = requests.post(
                f"{self.bridge_url}/api/notifications",
                json={"target": self.target, "message": message},
                timeout=5
            )
            if response.status_code == 200:
                logger.info("Notification successfully sent to Hermes.")
                return True
            else:
                logger.error(f"Hermes bridge returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification to Hermes: {e}")
            return False
```

**Step 3: Run test**
Run:
```powershell
pytest apps/backend/tests/test_hermes_service.py -v
```
Expected: PASS

**Step 4: Commit**
```bash
git add apps/backend/app/services/hermes_service.py apps/backend/tests/test_hermes_service.py
git commit -m "feat: implement Hermes notification service client"
```

---

### Task 5: Setup PostgreSQL MCP Configuration Guide

**Files:**
- Create: `docs/06-Maintenance/postgres-mcp-setup.md`

**Step 1: Write setup guide**
Create `docs/06-Maintenance/postgres-mcp-setup.md` with:
- Installation command: `npm install -g @modelcontextprotocol/server-postgres`
- Environment variables mapping configuration for cursor config settings.
- Verification queries to check table health.

**Step 2: Commit**
```bash
git add docs/06-Maintenance/postgres-mcp-setup.md
git commit -m "docs: add postgres-mcp-setup guide"
```
