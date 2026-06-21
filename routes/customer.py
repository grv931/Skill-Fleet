from functools import wraps
# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Service, ServiceRequest, Review
from forms import ServiceRequestForm, ReviewForm, SearchForm
from datetime import datetime

customer = Blueprint('customer', __name__, url_prefix='/customer')


def customer_required(f):
    """Decorator to restrict access to customer users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'customer':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ─── Dashboard ───────────────────────────────────────────────

@customer.route('/dashboard')
@customer_required
def dashboard():
    active_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id
    ).filter(ServiceRequest.service_status.in_(['requested', 'assigned'])).order_by(
        ServiceRequest.date_of_request.desc()
    ).all()

    closed_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id,
        service_status='closed'
    ).order_by(ServiceRequest.date_of_completion.desc()).limit(5).all()

    total_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).count()
    total_closed = ServiceRequest.query.filter_by(customer_id=current_user.id, service_status='closed').count()

    return render_template('customer/dashboard.html',
                           active_requests=active_requests,
                           closed_requests=closed_requests,
                           total_requests=total_requests,
                           total_closed=total_closed)


# ─── Search Services ────────────────────────────────────────

@customer.route('/search')
@customer_required
def search():
    form = SearchForm()
    query = request.args.get('query', '').strip()
    search_type = request.args.get('search_type', 'name')
    services = []

    if query:
        if search_type == 'name':
            services = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
        elif search_type == 'pin_code':
            # Find services that have professionals in the given pin code area
            professional_service_ids = db.session.query(User.service_type_id).filter(
                User.role == 'professional',
                User.is_approved == True,
                User.is_active == True,
                User.pin_code.ilike(f'%{query}%')
            ).distinct().subquery()
            services = Service.query.filter(Service.id.in_(professional_service_ids)).all()
        elif search_type == 'service':
            services = Service.query.filter(
                db.or_(
                    Service.name.ilike(f'%{query}%'),
                    Service.category.ilike(f'%{query}%'),
                    Service.description.ilike(f'%{query}%')
                )
            ).all()
    else:
        # Show all services by default
        services = Service.query.order_by(Service.name).all()

    return render_template('customer/search.html', form=form, services=services,
                           query=query, search_type=search_type)


# ─── Service Request CRUD ───────────────────────────────────

@customer.route('/request/new/<int:service_id>', methods=['GET', 'POST'])
@customer_required
def create_request(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceRequestForm()

    if form.validate_on_submit():
        sr = ServiceRequest(
            service_id=service.id,
            customer_id=current_user.id,
            preferred_date=form.preferred_date.data,
            customer_address=form.customer_address.data,
            customer_pin_code=form.customer_pin_code.data,
            remarks=form.remarks.data,
            service_status='requested'
        )
        db.session.add(sr)
        db.session.commit()
        flash(f'Service request for "{service.name}" created successfully!', 'success')
        return redirect(url_for('customer.my_requests'))

    # Pre-fill address and pin code from user profile
    if request.method == 'GET':
        form.customer_address.data = current_user.address
        form.customer_pin_code.data = current_user.pin_code

    return render_template('customer/service_request_form.html', form=form, service=service, title='New Service Request')


@customer.route('/request/<int:request_id>/edit', methods=['GET', 'POST'])
@customer_required
def edit_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.customer_id != current_user.id:
        abort(403)
    if sr.service_status != 'requested':
        flash('You can only edit requests that have not been accepted yet.', 'warning')
        return redirect(url_for('customer.my_requests'))

    form = ServiceRequestForm(obj=sr)
    if form.validate_on_submit():
        sr.preferred_date = form.preferred_date.data
        sr.customer_address = form.customer_address.data
        sr.customer_pin_code = form.customer_pin_code.data
        sr.remarks = form.remarks.data
        db.session.commit()
        flash('Service request updated successfully!', 'success')
        return redirect(url_for('customer.my_requests'))

    return render_template('customer/service_request_form.html', form=form, service=sr.service, title='Edit Service Request')


@customer.route('/request/<int:request_id>/close', methods=['POST'])
@customer_required
def close_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.customer_id != current_user.id:
        abort(403)
    if sr.service_status not in ['assigned']:
        flash('You can only close requests that are currently assigned.', 'warning')
        return redirect(url_for('customer.my_requests'))

    sr.service_status = 'closed'
    sr.date_of_completion = datetime.utcnow()
    db.session.commit()
    flash('Service request closed. Please leave a review!', 'success')
    return redirect(url_for('customer.review_request', request_id=request_id))


# ─── My Requests ────────────────────────────────────────────

@customer.route('/requests')
@customer_required
def my_requests():
    all_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id
    ).order_by(ServiceRequest.date_of_request.desc()).all()
    return render_template('customer/my_requests.html', requests=all_requests)


# ─── Reviews ────────────────────────────────────────────────

@customer.route('/request/<int:request_id>/review', methods=['GET', 'POST'])
@customer_required
def review_request(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    if sr.customer_id != current_user.id:
        abort(403)
    if sr.service_status != 'closed':
        flash('You can only review closed requests.', 'warning')
        return redirect(url_for('customer.my_requests'))
    if sr.review:
        flash('You have already reviewed this service.', 'info')
        return redirect(url_for('customer.my_requests'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            service_request_id=sr.id,
            customer_id=current_user.id,
            professional_id=sr.professional_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('customer.my_requests'))

    return render_template('customer/review_form.html', form=form, service_request=sr)
