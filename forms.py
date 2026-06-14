from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    IntegerField, FloatField, SubmitField, DateField
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo


class LoginForm(FlaskForm):
    """Login form for all user types."""
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Login')


class CustomerRegisterForm(FlaskForm):
    """Registration form for customers."""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    pin_code = StringField('Pin Code', validators=[DataRequired(), Length(min=4, max=10)])
    submit = SubmitField('Register')


class ProfessionalRegisterForm(FlaskForm):
    """Registration form for service professionals."""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    pin_code = StringField('Pin Code', validators=[DataRequired(), Length(min=4, max=10)])
    service_type = SelectField('Service Type', coerce=int, validators=[DataRequired()])
    experience = IntegerField('Experience (years)', validators=[DataRequired(), NumberRange(min=0, max=50)])
    description = TextAreaField('About Yourself / Qualifications', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Register')


class ServiceForm(FlaskForm):
    """Form for creating/editing a service (admin)."""
    name = StringField('Service Name', validators=[DataRequired(), Length(max=120)])
    base_price = FloatField('Base Price (₹)', validators=[DataRequired(), NumberRange(min=0)])
    time_required = IntegerField('Time Required (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    category = StringField('Category', validators=[Optional(), Length(max=60)])
    submit = SubmitField('Save Service')


class ServiceRequestForm(FlaskForm):
    """Form for creating a service request (customer)."""
    preferred_date = DateField('Preferred Date', validators=[DataRequired()])
    customer_address = TextAreaField('Service Address', validators=[DataRequired()])
    customer_pin_code = StringField('Pin Code', validators=[DataRequired(), Length(min=4, max=10)])
    remarks = TextAreaField('Remarks / Special Instructions', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Request')


class ReviewForm(FlaskForm):
    """Form for reviewing a completed service."""
    rating = SelectField('Rating', coerce=int,
                         choices=[(5, '★★★★★ Excellent'), (4, '★★★★ Very Good'),
                                  (3, '★★★ Good'), (2, '★★ Fair'), (1, '★ Poor')],
                         validators=[DataRequired()])
    comment = TextAreaField('Your Review', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')


class SearchForm(FlaskForm):
    """Search form used by customers and admin."""
    query = StringField('Search', validators=[DataRequired(), Length(max=120)])
    search_type = SelectField('Search By', choices=[
        ('name', 'Name'),
        ('pin_code', 'Pin Code'),
        ('service', 'Service Type')
    ])
    submit = SubmitField('Search')
