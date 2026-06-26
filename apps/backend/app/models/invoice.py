from sqlalchemy import Column, Integer, String, Date, Float, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.invoice_status import InvoiceStatus

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
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
