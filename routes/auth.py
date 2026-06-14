# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Service
from forms import LoginForm, CustomerRegisterForm, ProfessionalRegisterForm

auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    """Landing page — redirect to dashboard if logged in, else to login."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'professional':
            return redirect(url_for('professional.dashboard'))
        else:
            return redirect(url_for('customer.dashboard'))
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been blocked. Please contact admin.', 'danger')
                return render_template('auth/login.html', form=form)
            if user.role == 'professional' and not user.is_approved:
                flash('Your account is pending admin approval. Please wait.', 'warning')
                return render_template('auth/login.html', form=form)
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'professional':
                return redirect(url_for('professional.dashboard'))
            else:
                return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = CustomerRegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', form=form, role='customer')

        # Generate unique username from email
        import re
        base_username = form.email.data.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
        if not base_username:
            base_username = "user"
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=form.email.data,
            role='customer',
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            pin_code=form.pin_code.data,
            is_active=True,
            is_approved=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, role='customer')


@auth.route('/register/professional', methods=['GET', 'POST'])
def register_professional():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = ProfessionalRegisterForm()
    # Populate service type choices
    form.service_type.choices = [(s.id, s.name) for s in Service.query.order_by(Service.name).all()]

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', form=form, role='professional')

        # Generate unique username from email
        import re
        base_username = form.email.data.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
        if not base_username:
            base_username = "user"
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=form.email.data,
            role='professional',
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            pin_code=form.pin_code.data,
            service_type_id=form.service_type.data,
            experience=form.experience.data,
            description=form.description.data,
            is_active=True,
            is_approved=False  # Needs admin approval
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Your profile is pending admin approval.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, role='professional')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
