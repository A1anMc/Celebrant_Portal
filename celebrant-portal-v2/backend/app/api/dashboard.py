from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.couple import Couple
from app.models.ceremony import Ceremony
from app.models.invoice import Invoice
from app.models.legal_form import LegalForm
from app.auth.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get key dashboard metrics and statistics."""
    try:
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        
        # Core metrics
        total_couples = db.query(Couple).filter(Couple.user_id == current_user.id).count()
        
        active_couples = db.query(Couple).filter(
            and_(
                Couple.user_id == current_user.id,
                Couple.status.in_(["booked", "confirmed"])
            )
        ).count()
        
        # Upcoming ceremonies (next 30 days)
        upcoming_ceremonies = db.query(Ceremony).filter(
            and_(
                Ceremony.user_id == current_user.id,
                Ceremony.ceremony_date >= today,
                Ceremony.ceremony_date <= today + timedelta(days=30),
                Ceremony.status.in_(["planned", "confirmed"])
            )
        ).count()
        
        # Recent inquiries (last 30 days)
        recent_inquiries = db.query(Couple).filter(
            and_(
                Couple.user_id == current_user.id,
                Couple.status == "inquiry",
                Couple.created_at >= thirty_days_ago
            )
        ).count()
        
        # Revenue metrics
        total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.status == "paid"
            )
        ).scalar() or 0
        
        monthly_revenue = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.status == "paid",
                Invoice.paid_date >= thirty_days_ago
            )
        ).scalar() or 0
        
        # Outstanding invoices
        outstanding_invoices = db.query(func.count(Invoice.id), func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.status.in_(["sent", "viewed"])
            )
        ).first()
        
        outstanding_count = outstanding_invoices[0] or 0
        outstanding_amount = outstanding_invoices[1] or 0
        
        # Overdue invoices
        overdue_invoices = db.query(func.count(Invoice.id), func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.status.in_(["sent", "viewed"]),
                Invoice.due_date < today
            )
        ).first()
        
        overdue_count = overdue_invoices[0] or 0
        overdue_amount = overdue_invoices[1] or 0
        
        # Legal forms requiring attention
        urgent_legal_forms = db.query(LegalForm).filter(
            and_(
                LegalForm.user_id == current_user.id,
                LegalForm.status.in_(["required", "submitted"]),
                or_(
                    LegalForm.deadline_date <= today + timedelta(days=7),
                    LegalForm.expiry_date <= today + timedelta(days=30)
                )
            )
        ).count()
        
        return {
            "couples": {
                "total": total_couples,
                "active": active_couples,
                "recent_inquiries": recent_inquiries
            },
            "ceremonies": {
                "upcoming_30_days": upcoming_ceremonies
            },
            "revenue": {
                "total": float(total_revenue),
                "monthly": float(monthly_revenue),
                "outstanding_count": outstanding_count,
                "outstanding_amount": float(outstanding_amount),
                "overdue_count": overdue_count,
                "overdue_amount": float(overdue_amount)
            },
            "legal_forms": {
                "urgent_attention": urgent_legal_forms
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard metrics"
        )


@router.get("/upcoming-weddings")
async def get_upcoming_weddings(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upcoming weddings summary - your command centre."""
    try:
        today = date.today()
        end_date = today + timedelta(days=days)
        
        # Get upcoming ceremonies with couple details
        upcoming_ceremonies = db.query(Ceremony).join(Couple).filter(
            and_(
                Ceremony.user_id == current_user.id,
                Ceremony.ceremony_date >= today,
                Ceremony.ceremony_date <= end_date,
                Ceremony.status.in_(["planned", "confirmed"])
            )
        ).order_by(Ceremony.ceremony_date.asc()).all()
        
        ceremonies_data = []
        for ceremony in upcoming_ceremonies:
            ceremonies_data.append({
                "id": ceremony.id,
                "couple": {
                    "id": ceremony.couple.id,
                    "names": ceremony.couple.full_names,
                    "primary_email": ceremony.couple.primary_email,
                    "primary_phone": ceremony.couple.primary_phone
                },
                "ceremony": {
                    "date": ceremony.ceremony_date,
                    "time": ceremony.ceremony_time,
                    "venue": ceremony.venue_name,
                    "venue_address": ceremony.venue_address,
                    "type": ceremony.ceremony_type,
                    "guest_count": ceremony.guest_count,
                    "status": ceremony.status,
                    "days_until": ceremony.days_until_ceremony
                },
                "total_fee": float(ceremony.total_fee or 0)
            })
        
        # Summary statistics
        summary = {
            "total_ceremonies": len(ceremonies_data),
            "this_week": len([c for c in ceremonies_data if c["ceremony"]["days_until"] <= 7]),
            "next_week": len([c for c in ceremonies_data if 7 < c["ceremony"]["days_until"] <= 14]),
            "this_month": len([c for c in ceremonies_data if c["ceremony"]["days_until"] <= 30]),
            "total_revenue": sum([c["total_fee"] for c in ceremonies_data])
        }
        
        return {
            "summary": summary,
            "ceremonies": ceremonies_data
        }
    
    except Exception as e:
        logger.error(f"Error fetching upcoming weddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch upcoming weddings"
        )


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent activity feed for dashboard."""
    try:
        activities = []
        
        # Recent couples (last 7 days)
        recent_couples = db.query(Couple).filter(
            and_(
                Couple.user_id == current_user.id,
                Couple.created_at >= date.today() - timedelta(days=7)
            )
        ).order_by(Couple.created_at.desc()).limit(5).all()
        
        for couple in recent_couples:
            activities.append({
                "type": "couple_created",
                "title": f"New couple: {couple.full_names}",
                "description": f"Status: {couple.status.title()}",
                "timestamp": couple.created_at,
                "link": f"/couples/{couple.id}"
            })
        
        # Recent ceremonies
        recent_ceremonies = db.query(Ceremony).filter(
            and_(
                Ceremony.user_id == current_user.id,
                Ceremony.created_at >= date.today() - timedelta(days=7)
            )
        ).order_by(Ceremony.created_at.desc()).limit(3).all()
        
        for ceremony in recent_ceremonies:
            activities.append({
                "type": "ceremony_created",
                "title": f"Ceremony scheduled: {ceremony.couple.full_names}",
                "description": f"Date: {ceremony.ceremony_date}",
                "timestamp": ceremony.created_at,
                "link": f"/ceremonies/{ceremony.id}"
            })
        
        # Recent invoices
        recent_invoices = db.query(Invoice).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.created_at >= date.today() - timedelta(days=7)
            )
        ).order_by(Invoice.created_at.desc()).limit(3).all()
        
        for invoice in recent_invoices:
            activities.append({
                "type": "invoice_created",
                "title": f"Invoice created: {invoice.invoice_number}",
                "description": f"Amount: ${invoice.total_amount}",
                "timestamp": invoice.created_at,
                "link": f"/invoices/{invoice.id}"
            })
        
        # Sort all activities by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        return {"activities": activities}
    
    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recent activity"
        )


@router.get("/alerts")
async def get_dashboard_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get important alerts and notifications."""
    try:
        alerts = []
        today = date.today()
        
        # Overdue invoices
        overdue_invoices = db.query(Invoice).filter(
            and_(
                Invoice.user_id == current_user.id,
                Invoice.status.in_(["sent", "viewed"]),
                Invoice.due_date < today
            )
        ).count()
        
        if overdue_invoices > 0:
            alerts.append({
                "type": "warning",
                "title": "Overdue Invoices",
                "message": f"You have {overdue_invoices} overdue invoice(s)",
                "action": "View Invoices",
                "link": "/invoices?status=overdue"
            })
        
        # Urgent legal forms
        urgent_forms = db.query(LegalForm).filter(
            and_(
                LegalForm.user_id == current_user.id,
                LegalForm.status.in_(["required", "submitted"]),
                LegalForm.deadline_date <= today + timedelta(days=7)
            )
        ).count()
        
        if urgent_forms > 0:
            alerts.append({
                "type": "error",
                "title": "Urgent Legal Forms",
                "message": f"{urgent_forms} legal form(s) require immediate attention",
                "action": "View Legal Forms",
                "link": "/legal-forms?urgent=true"
            })
        
        # Ceremonies this week without NOIM
        ceremonies_this_week = db.query(Ceremony).filter(
            and_(
                Ceremony.user_id == current_user.id,
                Ceremony.ceremony_date >= today,
                Ceremony.ceremony_date <= today + timedelta(days=7),
                Ceremony.status.in_(["planned", "confirmed"])
            )
        ).all()
        
        ceremonies_without_noim = 0
        for ceremony in ceremonies_this_week:
            noim_exists = db.query(LegalForm).filter(
                and_(
                    LegalForm.ceremony_id == ceremony.id,
                    LegalForm.form_type == "noim",
                    LegalForm.status.in_(["submitted", "approved"])
                )
            ).first()
            
            if not noim_exists:
                ceremonies_without_noim += 1
        
        if ceremonies_without_noim > 0:
            alerts.append({
                "type": "warning",
                "title": "Missing NOIM Forms",
                "message": f"{ceremonies_without_noim} ceremony(ies) this week missing NOIM",
                "action": "Check Legal Forms",
                "link": "/legal-forms?type=noim"
            })
        
        return {"alerts": alerts}
    
    except Exception as e:
        logger.error(f"Error fetching dashboard alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard alerts"
        ) 