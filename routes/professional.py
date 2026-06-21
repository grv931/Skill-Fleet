from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, User, Service, ServiceRequest
from datetime import datetime

professional = Blueprint('professional', __name__, url_prefix='/professional')


def professional_required(f):
    """Decorator to restrict access to approved professional users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'professional':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ─── Dashboard ───────────────────────────────────────────────

@professional.route('/dashboard')
@professional_required
def dashboard():
    # Incoming requests for this professional's service type that are not yet assigned
    incoming_requests = ServiceRequest.query.filter_by(
        service_id=current_user.service_type_id,
        service_status='requested'
    ).order_by(ServiceRequest.date_of_request.desc()).all()

    # Requests assigned to this professional
    active_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        service_status='assigned'
    ).order_by(ServiceRequest.date_of_request.desc()).all()

    # Completed requests
    completed_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        service_status='closed'
    ).order_by(ServiceRequest.date_of_completion.desc()).limit(5).all()

    total_completed = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        service_status='closed'
    ).count()

    return render_template('professional/dashboard.html',
                           incoming_requests=incoming_requests,
                           active_requests=active_requests,
                           completed_requests=completed_requests,
                           total_completed=total_completed,
                           avg_rating=current_user.average_rating,
                           total_reviews=current_user.total_reviews)


# ─── All Requests ───────────────────────────────────────────

@professional.route('/requests')
@professional_required
def requests():
    # Show all requests matching this professional's service type
    incoming = ServiceRequest.query.filter_by(
        service_id=current_user.service_type_id,
        service_status='requested'
    ).order_by(ServiceRequest.date_of_request.desc()).all()

    my_assigned = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        service_status='assigned'
    ).order_by(ServiceRequest.date_of_request.desc()).all()

    my_closed = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        service_status='closed'
    ).order_by(ServiceRequest.date_of_completion.desc()).all()

    return render_template('professional/requests.html',
                           incoming=incoming,
                           my_assigned=my_assigned,
                           my_closed=my_closed)


# ─── Accept / Reject / Complete ─────────────────────────────

@professional.route('/requests/<int:request_id>/accept', methods=['POST'])
@professional_required
def accept_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.service_id != current_user.service_type_id:
        flash('This request is not for your service type.', 'danger')
        return redirect(url_for('professional.requests'))
    if sr.service_status != 'requested':
        flash('This request is no longer available.', 'warning')
        return redirect(url_for('professional.requests'))

    sr.professional_id = current_user.id
    sr.service_status = 'assigned'
    db.session.commit()
    flash('Service request accepted!', 'success')
    return redirect(url_for('professional.dashboard'))


@professional.route('/requests/<int:request_id>/reject', methods=['POST'])
@professional_required
def reject_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.professional_id != current_user.id:
        flash('You can only reject requests assigned to you.', 'danger')
        return redirect(url_for('professional.requests'))
    if sr.service_status != 'assigned':
        flash('This request cannot be rejected.', 'warning')
        return redirect(url_for('professional.requests'))

    sr.professional_id = None
    sr.service_status = 'requested'
    db.session.commit()
    flash('Service request rejected and returned to queue.', 'info')
    return redirect(url_for('professional.dashboard'))


@professional.route('/requests/<int:request_id>/complete', methods=['POST'])
@professional_required
def complete_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.professional_id != current_user.id:
        flash('You can only complete requests assigned to you.', 'danger')
        return redirect(url_for('professional.requests'))
    if sr.service_status != 'assigned':
        flash('This request cannot be completed.', 'warning')
        return redirect(url_for('professional.requests'))

    # Mark as closed (professional completes, customer closes)
    sr.service_status = 'closed'
    sr.date_of_completion = datetime.utcnow()
    db.session.commit()
    flash('Service request marked as complete!', 'success')
    return redirect(url_for('professional.dashboard'))


# ─── Profile ────────────────────────────────────────────────

@professional.route('/profile')
@professional_required
def profile():
    # Get reviews for this professional
    from models import Review
    reviews = Review.query.filter_by(professional_id=current_user.id).order_by(Review.date_created.desc()).all()
    return render_template('professional/profile.html', reviews=reviews)
