"""
Invoice routes for payment tracking and management.
"""
import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from models import db, Invoice, Couple, User

# Create blueprint
invoice_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

# Allowed file extensions for proof of payment
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@invoice_bp.route('/')
@login_required
def index():
    """List all invoices for the current organization."""
    try:
        # Get invoices for current user's organization
        invoices = Invoice.query.filter_by(
            organization_id=current_user.organization_id
        ).order_by(Invoice.due_date.desc()).all()
        
        # Calculate statistics
        total_invoices = len(invoices)
        paid_invoices = sum(1 for inv in invoices if inv.status == 'paid')
        pending_invoices = sum(1 for inv in invoices if inv.status == 'pending')
        overdue_invoices = sum(1 for inv in invoices if inv.is_overdue)
        
        total_amount = sum(inv.amount for inv in invoices)
        paid_amount = sum(inv.amount for inv in invoices if inv.status == 'paid')
        
        return render_template('invoices/index.html',
                             invoices=invoices,
                             total_invoices=total_invoices,
                             paid_invoices=paid_invoices,
                             pending_invoices=pending_invoices,
                             overdue_invoices=overdue_invoices,
                             total_amount=total_amount,
                             paid_amount=paid_amount)
    except Exception as e:
        current_app.logger.error(f"Error in invoice index: {str(e)}")
        flash('Error loading invoices', 'error')
        return redirect(url_for('index'))

@invoice_bp.route('/<int:invoice_id>')
@login_required
def view(invoice_id):
    """View a specific invoice."""
    try:
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            organization_id=current_user.organization_id
        ).first_or_404()
        
        return render_template('invoices/view.html', invoice=invoice)
    except Exception as e:
        current_app.logger.error(f"Error viewing invoice {invoice_id}: {str(e)}")
        flash('Error loading invoice', 'error')
        return redirect(url_for('invoices.index'))

@invoice_bp.route('/<int:invoice_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_proof(invoice_id):
    """Upload proof of payment for an invoice."""
    try:
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            organization_id=current_user.organization_id
        ).first_or_404()
        
        if request.method == 'POST':
            # Check if file was uploaded
            if 'proof_file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['proof_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Secure the filename
                filename = secure_filename(file.filename)
                
                # Create unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"proof_{invoice.invoice_number}_{timestamp}_{filename}"
                
                # Ensure upload directory exists
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'invoices')
                os.makedirs(upload_path, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_path, unique_filename)
                file.save(file_path)
                
                # Update invoice with proof of payment
                invoice.proof_of_payment_path = file_path
                invoice.proof_of_payment_filename = filename
                invoice.proof_of_payment_uploaded_at = datetime.utcnow()
                invoice.proof_of_payment_verified = False  # Reset verification
                
                db.session.commit()
                
                flash('Proof of payment uploaded successfully', 'success')
                return redirect(url_for('invoices.view', invoice_id=invoice.id))
            else:
                flash('Invalid file type. Allowed: pdf, png, jpg, jpeg, gif, doc, docx', 'error')
                return redirect(request.url)
        
        return render_template('invoices/upload_proof.html', invoice=invoice)
    except Exception as e:
        current_app.logger.error(f"Error uploading proof for invoice {invoice_id}: {str(e)}")
        flash('Error uploading proof of payment', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))

@invoice_bp.route('/<int:invoice_id>/mark_paid', methods=['POST'])
@login_required
def mark_paid(invoice_id):
    """Mark an invoice as paid (admin only)."""
    try:
        # Check if user has permission
        if not current_user.is_admin and current_user.role != 'owner':
            flash('Permission denied', 'error')
            return redirect(url_for('invoices.view', invoice_id=invoice_id))
        
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            organization_id=current_user.organization_id
        ).first_or_404()
        
        # Get paid amount from form
        paid_amount = request.form.get('paid_amount', type=float)
        if not paid_amount:
            paid_amount = invoice.amount
        
        # Mark as paid
        invoice.mark_as_paid(paid_amount=paid_amount, verified_by=current_user.id)
        db.session.commit()
        
        flash('Invoice marked as paid successfully', 'success')
        return redirect(url_for('invoices.view', invoice_id=invoice.id))
    except Exception as e:
        current_app.logger.error(f"Error marking invoice {invoice_id} as paid: {str(e)}")
        flash('Error marking invoice as paid', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))

@invoice_bp.route('/<int:invoice_id>/verify_proof', methods=['POST'])
@login_required
def verify_proof(invoice_id):
    """Verify proof of payment (admin only)."""
    try:
        # Check if user has permission
        if not current_user.is_admin and current_user.role != 'owner':
            flash('Permission denied', 'error')
            return redirect(url_for('invoices.view', invoice_id=invoice_id))
        
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            organization_id=current_user.organization_id
        ).first_or_404()
        
        if not invoice.proof_of_payment_path:
            flash('No proof of payment uploaded', 'error')
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
        
        # Verify the proof
        invoice.proof_of_payment_verified = True
        invoice.proof_of_payment_verified_by = current_user.id
        invoice.proof_of_payment_verified_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Proof of payment verified successfully', 'success')
        return redirect(url_for('invoices.view', invoice_id=invoice.id))
    except Exception as e:
        current_app.logger.error(f"Error verifying proof for invoice {invoice_id}: {str(e)}")
        flash('Error verifying proof of payment', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))

@invoice_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new invoice."""
    try:
        if request.method == 'POST':
            # Get form data
            couple_id = request.form.get('couple_id', type=int)
            amount = request.form.get('amount', type=float)
            description = request.form.get('description', '')
            due_date_str = request.form.get('due_date', '')
            
            # Validate required fields
            if not couple_id or not amount or not due_date_str:
                flash('Please fill in all required fields', 'error')
                return redirect(request.url)
            
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid due date format', 'error')
                return redirect(request.url)
            
            # Check if couple belongs to current organization
            couple = Couple.query.filter_by(
                id=couple_id,
                organization_id=current_user.organization_id
            ).first()
            
            if not couple:
                flash('Invalid couple selected', 'error')
                return redirect(request.url)
            
            # Create invoice
            invoice = Invoice(
                organization_id=current_user.organization_id,
                couple_id=couple_id,
                amount=amount,
                description=description,
                due_date=due_date,
                currency='AUD'  # Default to AUD
            )
            
            # Generate invoice number
            invoice.generate_invoice_number()
            
            db.session.add(invoice)
            db.session.commit()
            
            flash('Invoice created successfully', 'success')
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
        
        # Get couples for the current organization
        couples = Couple.query.filter_by(
            organization_id=current_user.organization_id
        ).order_by(Couple.partner1_name).all()
        
        return render_template('invoices/create.html', couples=couples)
    except Exception as e:
        current_app.logger.error(f"Error creating invoice: {str(e)}")
        flash('Error creating invoice', 'error')
        return redirect(url_for('invoices.index'))

@invoice_bp.route('/api/stats')
@login_required
def api_stats():
    """Get invoice statistics for dashboard."""
    try:
        # Get invoices for current organization
        invoices = Invoice.query.filter_by(
            organization_id=current_user.organization_id
        ).all()
        
        # Calculate statistics
        total_invoices = len(invoices)
        paid_invoices = sum(1 for inv in invoices if inv.status == 'paid')
        pending_invoices = sum(1 for inv in invoices if inv.status == 'pending')
        overdue_invoices = sum(1 for inv in invoices if inv.is_overdue)
        
        total_amount = sum(inv.amount for inv in invoices)
        paid_amount = sum(inv.amount for inv in invoices if inv.status == 'paid')
        
        # Get overdue invoices
        overdue_list = [
            {
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'couple_names': inv.couple.full_names,
                'amount': inv.amount,
                'due_date': inv.due_date.isoformat(),
                'days_overdue': abs(inv.days_until_due)
            }
            for inv in invoices if inv.is_overdue
        ]
        
        return jsonify({
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'pending_invoices': pending_invoices,
            'overdue_invoices': overdue_invoices,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'overdue_list': overdue_list
        })
    except Exception as e:
        current_app.logger.error(f"Error getting invoice stats: {str(e)}")
        return jsonify({'error': 'Error loading statistics'}), 500 