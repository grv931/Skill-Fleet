from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Single user table with role differentiation (admin / professional / customer)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin, professional, customer
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    pin_code = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # False = blocked
    # Professional-specific fields
    is_approved = db.Column(db.Boolean, default=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    experience = db.Column(db.Integer, default=0)  # years
    description = db.Column(db.Text)  # bio / profile docs description

    # Relationships
    service_type = db.relationship('Service', backref='professionals', foreign_keys=[service_type_id])
    customer_requests = db.relationship('ServiceRequest', backref='customer', foreign_keys='ServiceRequest.customer_id', lazy='dynamic')
    professional_requests = db.relationship('ServiceRequest', backref='professional', foreign_keys='ServiceRequest.professional_id', lazy='dynamic')
    reviews_given = db.relationship('Review', backref='reviewer', foreign_keys='Review.customer_id', lazy='dynamic')
    reviews_received = db.relationship('Review', backref='professional_reviewed', foreign_keys='Review.professional_id', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def total_reviews(self):
        return self.reviews_received.count()

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Service(db.Model):
    """A type of household service offered on the platform."""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, default=60)  # in minutes
    description = db.Column(db.Text)
    category = db.Column(db.String(60))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requests = db.relationship('ServiceRequest', backref='service', lazy='dynamic')

    def __repr__(self):
        return f'<Service {self.name}>'


class ServiceRequest(db.Model):
    """A request made by a customer for a particular service."""
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    preferred_date = db.Column(db.DateTime, nullable=True)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), default='requested')  # requested / assigned / closed
    remarks = db.Column(db.Text)
    customer_address = db.Column(db.Text)
    customer_pin_code = db.Column(db.String(10))

    # Relationship to review
    review = db.relationship('Review', backref='service_request', uselist=False)

    def __repr__(self):
        return f'<ServiceRequest #{self.id} ({self.service_status})>'


class Review(db.Model):
    """Review left by a customer after closing a service request."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review #{self.id} ({self.rating}/5)>'
