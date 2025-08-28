"""
Invoice service layer for business logic operations.
Handles all invoice-related business operations and data validation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime, timedelta
import uuid

from ..models import Invoice, Couple
from ..schemas import InvoiceCreate, InvoiceUpdate
from ..core.exceptions import (
    InvoiceNotFoundException,
    CoupleNotFoundException,
    ValidationException,
    DatabaseException
)


class InvoiceService:
    """Service class for invoice management operations."""
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{unique_id}"
    
    @staticmethod
    async def get_invoices(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        couple_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Invoice]:
        """
        Get invoices for a specific celebrant with filtering and pagination.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by invoice status
            couple_id: Filter by couple ID
            date_from: Filter by invoice date from
            date_to: Filter by invoice date to
            
        Returns:
            List of invoices matching the criteria
        """
        try:
            query = db.query(Invoice).join(Couple).filter(Couple.celebrant_id == user_id)
            
            # Apply status filter
            if status:
                query = query.filter(Invoice.status == status)
            
            # Apply couple filter
            if couple_id:
                query = query.filter(Invoice.couple_id == couple_id)
            
            # Apply date range filter
            if date_from:
                query = query.filter(Invoice.created_at >= date_from)
            if date_to:
                query = query.filter(Invoice.created_at <= date_to)
            
            # Apply pagination and ordering
            invoices = query.order_by(desc(Invoice.created_at)).offset(skip).limit(limit).all()
            
            return invoices
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve invoices: {str(e)}")
    
    @staticmethod
    async def get_invoice_by_id(db: Session, invoice_id: int, user_id: int) -> Invoice:
        """
        Get a specific invoice by ID, ensuring it belongs to the user.
        
        Args:
            db: Database session
            invoice_id: ID of the invoice
            user_id: ID of the celebrant
            
        Returns:
            Invoice object
            
        Raises:
            InvoiceNotFoundException: If invoice not found or doesn't belong to user
        """
        try:
            invoice = db.query(Invoice).join(Couple).filter(
                and_(
                    Invoice.id == invoice_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not invoice:
                raise InvoiceNotFoundException(str(invoice_id))
            
            return invoice
            
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve invoice: {str(e)}")
    
    @staticmethod
    async def create_invoice(db: Session, invoice_data: InvoiceCreate, user_id: int) -> Invoice:
        """
        Create a new invoice for a couple.
        
        Args:
            db: Database session
            invoice_data: Invoice creation data
            user_id: ID of the celebrant
            
        Returns:
            Created invoice object
            
        Raises:
            CoupleNotFoundException: If couple not found or doesn't belong to user
            ValidationException: If data validation fails
        """
        try:
            # Verify couple belongs to user
            couple = db.query(Couple).filter(
                and_(
                    Couple.id == invoice_data.couple_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not couple:
                raise CoupleNotFoundException(str(invoice_data.couple_id))
            
            # Validate invoice data
            if invoice_data.amount <= 0:
                raise ValidationException(
                    "Invoice amount must be greater than zero",
                    field="amount"
                )
            
            if invoice_data.due_date and invoice_data.due_date < datetime.now():
                raise ValidationException(
                    "Due date cannot be in the past",
                    field="due_date"
                )
            
            # Generate invoice number
            invoice_number = InvoiceService.generate_invoice_number()
            
            # Create invoice object
            invoice = Invoice(
                **invoice_data.dict(),
                invoice_number=invoice_number
            )
            
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            
            return invoice
            
        except (CoupleNotFoundException, ValidationException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to create invoice: {str(e)}")
    
    @staticmethod
    async def update_invoice(
        db: Session,
        invoice_id: int,
        invoice_data: InvoiceUpdate,
        user_id: int
    ) -> Invoice:
        """
        Update an existing invoice.
        
        Args:
            db: Database session
            invoice_id: ID of the invoice
            invoice_data: Invoice update data
            user_id: ID of the celebrant
            
        Returns:
            Updated invoice object
            
        Raises:
            InvoiceNotFoundException: If invoice not found
            ValidationException: If data validation fails
        """
        try:
            # Get existing invoice
            invoice = await InvoiceService.get_invoice_by_id(db, invoice_id, user_id)
            
            # Validate amount if provided
            if invoice_data.amount is not None and invoice_data.amount <= 0:
                raise ValidationException(
                    "Invoice amount must be greater than zero",
                    field="amount"
                )
            
            # Validate due date if provided
            if invoice_data.due_date and invoice_data.due_date < datetime.now():
                raise ValidationException(
                    "Due date cannot be in the past",
                    field="due_date"
                )
            
            # Update invoice fields
            update_data = invoice_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(invoice, field, value)
            
            db.commit()
            db.refresh(invoice)
            
            return invoice
            
        except (InvoiceNotFoundException, ValidationException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to update invoice: {str(e)}")
    
    @staticmethod
    async def delete_invoice(db: Session, invoice_id: int, user_id: int) -> bool:
        """
        Delete an invoice.
        
        Args:
            db: Database session
            invoice_id: ID of the invoice
            user_id: ID of the celebrant
            
        Returns:
            True if deletion was successful
            
        Raises:
            InvoiceNotFoundException: If invoice not found
        """
        try:
            # Get existing invoice
            invoice = await InvoiceService.get_invoice_by_id(db, invoice_id, user_id)
            
            db.delete(invoice)
            db.commit()
            
            return True
            
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to delete invoice: {str(e)}")
    
    @staticmethod
    async def mark_invoice_as_paid(db: Session, invoice_id: int, user_id: int) -> Invoice:
        """
        Mark an invoice as paid.
        
        Args:
            db: Database session
            invoice_id: ID of the invoice
            user_id: ID of the celebrant
            
        Returns:
            Updated invoice object
            
        Raises:
            InvoiceNotFoundException: If invoice not found
        """
        try:
            # Get existing invoice
            invoice = await InvoiceService.get_invoice_by_id(db, invoice_id, user_id)
            
            # Update invoice status
            invoice.status = "Paid"
            invoice.paid_date = datetime.now()
            
            db.commit()
            db.refresh(invoice)
            
            return invoice
            
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to mark invoice as paid: {str(e)}")
    
    @staticmethod
    async def get_invoice_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get invoice statistics for a celebrant.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            
        Returns:
            Dictionary with invoice statistics
        """
        try:
            # Total invoices
            total_invoices = db.query(Invoice).join(Couple).filter(
                Couple.celebrant_id == user_id
            ).count()
            
            # Total revenue
            total_revenue = db.query(func.sum(Invoice.amount)).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status == "Paid"
                )
            ).scalar() or 0
            
            # Count by status
            draft_count = db.query(Invoice).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status == "Draft"
                )
            ).count()
            
            sent_count = db.query(Invoice).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status == "Sent"
                )
            ).count()
            
            paid_count = db.query(Invoice).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status == "Paid"
                )
            ).count()
            
            overdue_count = db.query(Invoice).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status == "Overdue"
                )
            ).count()
            
            # Monthly revenue (last 12 months)
            monthly_revenue = []
            for i in range(12):
                month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                
                revenue = db.query(func.sum(Invoice.amount)).join(Couple).filter(
                    and_(
                        Couple.celebrant_id == user_id,
                        Invoice.status == "Paid",
                        Invoice.paid_date >= month_start,
                        Invoice.paid_date <= month_end
                    )
                ).scalar() or 0
                
                monthly_revenue.append({
                    "month": month_start.strftime("%Y-%m"),
                    "revenue": float(revenue)
                })
            
            return {
                "total_invoices": total_invoices,
                "total_revenue": float(total_revenue),
                "draft_count": draft_count,
                "sent_count": sent_count,
                "paid_count": paid_count,
                "overdue_count": overdue_count,
                "monthly_revenue": monthly_revenue
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve invoice statistics: {str(e)}")
    
    @staticmethod
    async def get_overdue_invoices(db: Session, user_id: int) -> List[Invoice]:
        """
        Get overdue invoices for a celebrant.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            
        Returns:
            List of overdue invoices
        """
        try:
            overdue_invoices = db.query(Invoice).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Invoice.status.in_(["Sent", "Draft"]),
                    Invoice.due_date < datetime.now()
                )
            ).order_by(Invoice.due_date).all()
            
            return overdue_invoices
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve overdue invoices: {str(e)}")
    
    @staticmethod
    async def send_invoice_reminder(db: Session, invoice_id: int, user_id: int) -> bool:
        """
        Send an invoice reminder (placeholder for email integration).
        
        Args:
            db: Database session
            invoice_id: ID of the invoice
            user_id: ID of the celebrant
            
        Returns:
            True if reminder was sent successfully
            
        Raises:
            InvoiceNotFoundException: If invoice not found
        """
        try:
            # Get existing invoice
            invoice = await InvoiceService.get_invoice_by_id(db, invoice_id, user_id)
            
            # Update invoice status to Sent if it's Draft
            if invoice.status == "Draft":
                invoice.status = "Sent"
                db.commit()
            
            # TODO: Implement actual email sending
            # For now, just log the action
            print(f"Reminder sent for invoice {invoice.invoice_number}")
            
            return True
            
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to send invoice reminder: {str(e)}")
