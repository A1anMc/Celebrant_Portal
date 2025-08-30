"""
Invoices API router.
Handles all invoice-related endpoints with proper error handling.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.database import get_db
from ...models import User
from ...schemas import InvoiceCreate, InvoiceUpdate, Invoice as InvoiceSchema
from ...core.auth import get_current_active_user
from ...services.invoice_service import InvoiceService
from ...core.exceptions import (
    InvoiceNotFoundException,
    CoupleNotFoundException,
    ValidationException,
    DatabaseException
)

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/", response_model=InvoiceSchema)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new invoice for a couple."""
    try:
        return await InvoiceService.create_invoice(db, invoice, current_user.id)
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[InvoiceSchema])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    couple_id: Optional[int] = Query(None, description="Filter by couple ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all invoices for the current celebrant with filtering and pagination."""
    try:
        return await InvoiceService.get_invoices(
            db, current_user.id, skip, limit, status, couple_id, date_from, date_to
        )
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/stats")
async def get_invoices_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get invoice statistics for the dashboard."""
    try:
        invoices = await InvoiceService.get_invoices(db, current_user.id, 0, 1000)
        
        # Calculate summary statistics
        total_invoices = len(invoices)
        total_amount = sum(invoice.total_amount for invoice in invoices if invoice.total_amount)
        paid_invoices = len([i for i in invoices if i.status == "paid"])
        pending_invoices = len([i for i in invoices if i.status == "pending"])
        
        return {
            "total_invoices": total_invoices,
            "total_amount": total_amount,
            "paid_invoices": paid_invoices,
            "pending_invoices": pending_invoices,
            "recent_invoices": invoices[:5]  # Last 5 invoices
        }
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{invoice_id}", response_model=InvoiceSchema)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific invoice by ID."""
    try:
        return await InvoiceService.get_invoice_by_id(db, invoice_id, current_user.id)
    except InvoiceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{invoice_id}", response_model=InvoiceSchema)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing invoice."""
    try:
        return await InvoiceService.update_invoice(db, invoice_id, invoice_update, current_user.id)
    except InvoiceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an invoice."""
    try:
        await InvoiceService.delete_invoice(db, invoice_id, current_user.id)
        return {"message": "Invoice deleted successfully"}
    except InvoiceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{invoice_id}/mark-paid", response_model=InvoiceSchema)
async def mark_invoice_as_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark an invoice as paid."""
    try:
        return await InvoiceService.mark_invoice_as_paid(db, invoice_id, current_user.id)
    except InvoiceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/statistics/", response_model=dict)
async def get_invoice_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get invoice statistics for the current celebrant."""
    try:
        return await InvoiceService.get_invoice_statistics(db, current_user.id)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/overdue/", response_model=List[InvoiceSchema])
async def get_overdue_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get overdue invoices for the current celebrant."""
    try:
        return await InvoiceService.get_overdue_invoices(db, current_user.id)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{invoice_id}/send-reminder")
async def send_invoice_reminder(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send an invoice reminder."""
    try:
        await InvoiceService.send_invoice_reminder(db, invoice_id, current_user.id)
        return {"message": "Invoice reminder sent successfully"}
    except InvoiceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))