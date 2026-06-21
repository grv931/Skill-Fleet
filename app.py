import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User

# ─── App Factory ─────────────────────────────────────────────

app = Flask(__name__)
app.config['SECRET_KEY'] = 'skillfleet-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillfleet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─── Register Blueprints ────────────────────────────────────

from routes.auth import auth
from routes.admin import admin
from routes.customer import customer
from routes.professional import professional
from api import api

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(customer)
app.register_blueprint(professional)
app.register_blueprint(api)


# ─── Error Handlers ─────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


# ─── Seed Admin User ────────────────────────────────────────

def seed_admin():
    """Create admin user if it doesn't exist."""
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@skillfleet.com',
            role='admin',
            name='Administrator',
            is_active=True,
            is_approved=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print(' * Admin user created (email: admin@skillfleet.com, password: admin123)')


# ─── Initialize Database & Seed Admin ───────────────────────
with app.app_context():
    db.create_all()
    seed_admin()

# ─── Main ────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
