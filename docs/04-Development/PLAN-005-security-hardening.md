# Security Hardening (JWT Auth, CORS & Rate Limiting) Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Secure the FastAPI backend by adding user authentication (JWT), password hashing (bcrypt), origin restrictions (CORS), and API rate limiting (SlowAPI) to prevent resource abuse.

**Architecture:** 
1. Introduce a `User` entity to the database for account-based storage.
2. Build an `auth_service` providing JWT generation/verification and password hashing.
3. Protect the `invoices` routes via FastAPI dependency injection (`get_current_user`).
4. Configure CORS middleware in `main.py` to whitelist specific domains (e.g., Next.js frontend origin).
5. Integrate SlowAPI rate limiter in FastAPI to limit request throughput.

**Tech Stack Additions:**
* `PyJWT==2.8.0` (Token-based authentication)
* `bcrypt==4.1.3` (Secure password hashing)
* `slowapi==0.1.9` (FastAPI rate limiting)

---

### Task 1: Initialize User database entities & schemas

**Files:**
- Create: `apps/backend/app/models/user.py`
- Create: `apps/backend/app/schemas/user.py`
- Modify: `apps/backend/app/models/__init__.py`
- Test: `apps/backend/tests/test_user_models.py`

**Step 1: Write a failing database model test**
Create `apps/backend/tests/test_user_models.py` testing user creation:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db_session):
    user = User(username="admin", hashed_password="hashed_placeholder_string", role="admin")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.username == "admin"
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_user_models.py -v
```
Expected: FAIL (ImportError - missing User model).

**Step 3: Write minimal implementation**
1. Append dependencies to `apps/backend/requirements.txt`:
```
PyJWT==2.8.0
bcrypt==4.1.3
slowapi==0.1.9
```

2. Create `apps/backend/app/models/user.py`:
```python
from sqlalchemy import Column, BigInteger, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
```

3. Create `apps/backend/app/schemas/user.py`:
```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
```

4. Register the new model in `apps/backend/app/models/__init__.py`:
```python
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.invoice_status import InvoiceStatus
from app.models.user import User
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pip install -r apps/backend/requirements.txt
pytest apps/backend/tests/test_user_models.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/requirements.txt apps/backend/app/models/user.py apps/backend/app/schemas/user.py apps/backend/tests/test_user_models.py
git commit -m "feat: add user model and schemas for JWT authentication"
```

---

### Task 2: Implement Cryptography & Token Service

**Files:**
- Create: `apps/backend/app/services/auth_service.py`
- Test: `apps/backend/tests/test_auth_service.py`

**Step 1: Write a failing service test**
Create `apps/backend/tests/test_auth_service.py` verifying hash matching and token encoding/decoding:
```python
import pytest
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    pwd = "secretpassword"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_lifecycle():
    token = create_access_token(data={"sub": "admin", "role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "admin"
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_auth_service.py -v
```
Expected: FAIL (missing service module).

**Step 3: Write minimal implementation**
Create `apps/backend/app/services/auth_service.py`:
```python
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_dev_secret_key_32_bytes_long_random")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest apps/backend/tests/test_auth_service.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/app/services/auth_service.py apps/backend/tests/test_auth_service.py
git commit -m "feat: implement bcrypt hashing and jwt lifecycle service"
```

---

### Task 3: Configure Auth Routes & Protect Invoices Router

**Files:**
- Create: `apps/backend/app/routers/auth.py`
- Modify: `apps/backend/app/routers/invoices.py`
- Modify: `apps/backend/main.py`
- Test: `apps/backend/tests/test_auth_endpoints.py`

**Step 1: Write failing integration test**
Verify `/api/invoices/health` is public, but file upload and history endpoints require a valid JWT token (return HTTP 401):
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check_remains_public():
    res = client.get("/api/invoices/health")
    assert res.status_code == 200

def test_invoices_protected_by_default():
    res = client.get("/api/invoices")
    assert res.status_code == 401  # Unauthorized
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_auth_endpoints.py -v
```
Expected: FAIL (endpoints return 200/404 instead of 401).

**Step 3: Write minimal implementation**
1. Add dependencies to protect routes in `apps/backend/app/routers/invoices.py`.
Create dependency helper:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
```
Add to routes:
```python
@router.get("", dependencies=[Depends(get_current_user)])
def list_invoices():
    # Fetch invoices...
    pass
```

2. Create Auth Router `apps/backend/app/routers/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = hash_password(user_in.password)
    user = User(username=user_in.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
```

3. Include Auth Router in `apps/backend/main.py`:
```python
from app.routers.auth import router as auth_router
app.include_router(auth_router)
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest apps/backend/tests/test_auth_endpoints.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/app/routers/auth.py apps/backend/app/routers/invoices.py apps/backend/main.py apps/backend/tests/test_auth_endpoints.py
git commit -m "feat: implement auth router endpoints and restrict invoices endpoints"
```

---

### Task 4: Setup CORS & API Rate Limiting

**Files:**
- Modify: `apps/backend/main.py`
- Test: `apps/backend/tests/test_security_headers.py`

**Step 1: Write failing test checking CORS & rate limit response**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cors_headers_present():
    response = client.options("/api/invoices/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
```

**Step 2: Run test to verify it fails**
Run:
```powershell
pytest apps/backend/tests/test_security_headers.py -v
```
Expected: FAIL (missing CORS access control headers).

**Step 3: Write minimal implementation**
Modify `apps/backend/main.py` to add CORS middleware and SlowAPI:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="OCR Invoice Processing API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Restrict CORS to authorized frontend domain
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 4: Run test to verify it passes**
Run:
```powershell
pytest apps/backend/tests/test_security_headers.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add apps/backend/main.py apps/backend/tests/test_security_headers.py
git commit -m "feat: implement strict CORS configuration and rate limit handlers"
```
