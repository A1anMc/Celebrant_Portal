from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice Information
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    
    # Client Information
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False)
    couple = relationship("Couple", back_populates="invoices")
    
    # Financial Information
    subtotal = Column(Numeric(10, 2), default=0)
    gst_rate = Column(Numeric(5, 2), default=10.0)  # GST percentage
    gst_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)
    
    # Payment Information
    status = Column(String(50), default="draft", index=True)
    # draft, sent, viewed, paid, overdue, cancelled, refunded
    payment_method = Column(String(50))  # bank_transfer, card, cash, cheque
    payment_reference = Column(String(100))
    paid_amount = Column(Numeric(10, 2), default=0)
    paid_date = Column(Date)
    
    # Additional Information
    notes = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invoices")
    
    ceremony_id = Column(Integer, ForeignKey("ceremonies.id"))
    ceremony = relationship("Ceremony", back_populates="invoices")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True))
    viewed_at = Column(DateTime(timezone=True))
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        from datetime import date
        return self.due_date < date.today() and self.status not in ["paid", "cancelled", "refunded"]
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        from datetime import date
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return (self.total_amount or 0) - (self.paid_amount or 0)
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Item Information
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Tax Information
    is_taxable = Column(Boolean, default=True)
    tax_rate = Column(Numeric(5, 2), default=10.0)
    
    # Relationships
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice = relationship("Invoice", back_populates="items")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, description='{self.description}', total='{self.total_price}')>"


# Add relationships to other models
Invoice.items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

from .couple import Couple
Couple.invoices = relationship("Invoice", back_populates="couple")

from .user import User
User.invoices = relationship("Invoice", back_populates="user")

from .ceremony import Ceremony
Ceremony.invoices = relationship("Invoice", back_populates="ceremony") 