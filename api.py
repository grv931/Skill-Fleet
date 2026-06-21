
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import db, User, Service, ServiceRequest, Review
from sqlalchemy import func

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/services')
def get_services():
    """List all available services."""
    services = Service.query.order_by(Service.name).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'base_price': s.base_price,
        'time_required': s.time_required,
        'description': s.description,
        'category': s.category
    } for s in services])


@api.route('/services/<int:service_id>')
def get_service(service_id):
    """Get a single service's details."""
    s = Service.query.get_or_404(service_id)
    professional_count = User.query.filter_by(
        role='professional', service_type_id=s.id, is_approved=True, is_active=True
    ).count()
    return jsonify({
        'id': s.id,
        'name': s.name,
        'base_price': s.base_price,
        'time_required': s.time_required,
        'description': s.description,
        'category': s.category,
        'available_professionals': professional_count
    })


@api.route('/stats')
@login_required
def get_stats():
    """Dashboard statistics for ChartJS (admin only)."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    # Requests by status
    requested = ServiceRequest.query.filter_by(service_status='requested').count()
    assigned = ServiceRequest.query.filter_by(service_status='assigned').count()
    closed = ServiceRequest.query.filter_by(service_status='closed').count()

    # Requests per service
    service_stats = db.session.query(
        Service.name,
        func.count(ServiceRequest.id)
    ).outerjoin(ServiceRequest, Service.id == ServiceRequest.service_id)\
     .group_by(Service.name).all()

    # Top professionals by rating
    top_professionals = db.session.query(
        User.name,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(Review, User.id == Review.professional_id)\
     .group_by(User.name)\
     .order_by(func.avg(Review.rating).desc())\
     .limit(5).all()

    return jsonify({
        'requests_by_status': {
            'labels': ['Requested', 'Assigned', 'Closed'],
            'data': [requested, assigned, closed]
        },
        'requests_per_service': {
            'labels': [s[0] for s in service_stats],
            'data': [s[1] for s in service_stats]
        },
        'top_professionals': {
            'labels': [p[0] for p in top_professionals],
            'ratings': [round(float(p[1]), 1) for p in top_professionals],
            'review_counts': [p[2] for p in top_professionals]
        }
    })


@api.route('/professionals')
def get_professionals():
    """List all approved, active professionals with ratings."""
    professionals = User.query.filter_by(
        role='professional', is_approved=True, is_active=True
    ).all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'service_type': p.service_type.name if p.service_type else None,
        'experience': p.experience,
        'average_rating': p.average_rating,
        'total_reviews': p.total_reviews,
        'pin_code': p.pin_code
    } for p in professionals])
