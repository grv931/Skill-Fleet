from functools import wraps
# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Service, ServiceRequest, Review
from forms import ServiceForm, SearchForm

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ─── Dashboard ───────────────────────────────────────────────

@admin.route('/dashboard')
@admin_required
def dashboard():
    total_services = Service.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_professionals = User.query.filter_by(role='professional').count()
    pending_approvals = User.query.filter_by(role='professional', is_approved=False, is_active=True).count()

    total_requests = ServiceRequest.query.count()
    requested_count = ServiceRequest.query.filter_by(service_status='requested').count()
    assigned_count = ServiceRequest.query.filter_by(service_status='assigned').count()
    closed_count = ServiceRequest.query.filter_by(service_status='closed').count()

    recent_requests = ServiceRequest.query.order_by(ServiceRequest.date_of_request.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_services=total_services,
                           total_customers=total_customers,
                           total_professionals=total_professionals,
                           pending_approvals=pending_approvals,
                           total_requests=total_requests,
                           requested_count=requested_count,
                           assigned_count=assigned_count,
                           closed_count=closed_count,
                           recent_requests=recent_requests)


# ─── Service Management ─────────────────────────────────────

@admin.route('/services')
@admin_required
def services():
    all_services = Service.query.order_by(Service.name).all()
    return render_template('admin/services.html', services=all_services)


@admin.route('/services/new', methods=['GET', 'POST'])
@admin_required
def create_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data,
            description=form.description.data,
            category=form.category.data
        )
        db.session.add(service)
        db.session.commit()
        flash(f'Service "{service.name}" created successfully!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/service_form.html', form=form, title='Create New Service')


@admin.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        service.description = form.description.data
        service.category = form.category.data
        db.session.commit()
        flash(f'Service "{service.name}" updated successfully!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/service_form.html', form=form, title='Edit Service', service=service)


@admin.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    # Check if service has active requests
    active_requests = ServiceRequest.query.filter(
        ServiceRequest.service_id == service_id,
        ServiceRequest.service_status.in_(['requested', 'assigned'])
    ).count()
    if active_requests > 0:
        flash(f'Cannot delete "{service.name}" — it has {active_requests} active request(s).', 'danger')
        return redirect(url_for('admin.services'))
    db.session.delete(service)
    db.session.commit()
    flash(f'Service "{service.name}" deleted.', 'success')
    return redirect(url_for('admin.services'))


# ─── Professional Management ────────────────────────────────

@admin.route('/professionals')
@admin_required
def professionals():
    all_professionals = User.query.filter_by(role='professional').order_by(User.date_created.desc()).all()
    return render_template('admin/professionals.html', professionals=all_professionals)


@admin.route('/professionals/<int:user_id>/approve', methods=['POST'])
@admin_required
def approve_professional(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'professional':
        abort(404)
    user.is_approved = True
    db.session.commit()
    flash(f'Professional "{user.name}" has been approved.', 'success')
    return redirect(url_for('admin.professionals'))


@admin.route('/professionals/<int:user_id>/block', methods=['POST'])
@admin_required
def toggle_block_professional(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'professional':
        abort(404)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'unblocked' if user.is_active else 'blocked'
    flash(f'Professional "{user.name}" has been {status}.', 'success')
    return redirect(url_for('admin.professionals'))


# ─── Customer Management ────────────────────────────────────

@admin.route('/customers')
@admin_required
def customers():
    all_customers = User.query.filter_by(role='customer').order_by(User.date_created.desc()).all()
    return render_template('admin/customers.html', customers=all_customers)


@admin.route('/customers/<int:user_id>/block', methods=['POST'])
@admin_required
def toggle_block_customer(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'customer':
        abort(404)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'unblocked' if user.is_active else 'blocked'
    flash(f'Customer "{user.name}" has been {status}.', 'success')
    return redirect(url_for('admin.customers'))


# ─── Search ─────────────────────────────────────────────────

@admin.route('/search')
@admin_required
def search():
    form = SearchForm()
    results = []
    search_type = request.args.get('search_type', 'name')
    query = request.args.get('query', '').strip()

    if query:
        if search_type == 'name':
            results = User.query.filter(
                User.role.in_(['customer', 'professional']),
                User.name.ilike(f'%{query}%')
            ).all()
        elif search_type == 'pin_code':
            results = User.query.filter(
                User.role.in_(['customer', 'professional']),
                User.pin_code.ilike(f'%{query}%')
            ).all()
        elif search_type == 'service':
            results = User.query.filter(
                User.role == 'professional'
            ).join(Service, User.service_type_id == Service.id).filter(
                Service.name.ilike(f'%{query}%')
            ).all()

    return render_template('admin/search.html', form=form, results=results,
                           query=query, search_type=search_type)
