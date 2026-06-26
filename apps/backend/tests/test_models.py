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
