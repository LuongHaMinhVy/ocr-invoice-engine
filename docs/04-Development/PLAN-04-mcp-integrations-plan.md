# Email Intake & PostgreSQL MCP Integrations Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implement automated invoice intake by polling email attachments via Python IMAP (using APScheduler) and set up PostgreSQL MCP server for database validation.

**Architecture:** Initialize APScheduler in Flask, schedule an EmailIntakeService that connects via IMAP to poll unread emails for image/PDF attachments, saves them to temporary storage, and routes them to the OCR engine. Configure Postgres MCP server in settings.

**Tech Stack:** Python 3.11+, APScheduler, imaplib, email, PostgreSQL MCP.

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
git commit -m "feat: add Flask backend APScheduler dependencies"
```

---

### Task 2: Implement Mail Polling Scheduler Configuration

**Files:**
- Create: `apps/backend/app/scheduler/__init__.py`
- Create: `apps/backend/app/scheduler/jobs.py`
- Modify: `apps/backend/app/__init__.py`
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

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    # Poll every 5 minutes
    scheduler.add_job(email_polling_job, 'interval', minutes=5, id='email_poll_job')
    scheduler.start()
    return scheduler
```

3. Modify `apps/backend/app/__init__.py` to initialize the scheduler:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.scheduler import init_scheduler

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Initialize background scheduler (skip in testing mode)
    if not app.config.get("TESTING"):
        init_scheduler(app)

    from app.routes.invoices import invoices_bp
    app.register_blueprint(invoices_bp, url_prefix="/api/invoices")

    return app
```

**Step 3: Run test to verify passes**
Run:
```powershell
pytest apps/backend/tests/test_scheduler.py -v
```
Expected: PASS

**Step 4: Commit**
```bash
git add apps/backend/app/scheduler/ apps/backend/app/__init__.py apps/backend/tests/test_scheduler.py
git commit -m "feat: configure background APScheduler for email polling"
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

### Task 4: Setup PostgreSQL MCP Configuration Guide

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
