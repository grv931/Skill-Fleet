import os
from datetime import datetime, timedelta
from app import app
from models import db, User, Service, ServiceRequest, Review

def seed_data():
    print("Recreating database tables...")
    db.drop_all()
    db.create_all()

    print("Adding admin user...")
    admin = User(
        username="admin",
        email="admin@skillfleet.com",
        role="admin",
        name="Administrator",
        is_active=True,
        is_approved=True
    )
    admin.set_password("admin123")
    db.session.add(admin)

    print("Adding services...")
    plumbing = Service(
        name="Plumbing Services",
        base_price=150.0,
        time_required=60,
        description="Fix leaks, taps, pipes, blockages, and install fixtures.",
        category="Plumbing"
    )
    electrical = Service(
        name="Electrical Repairs",
        base_price=200.0,
        time_required=45,
        description="Wiring, switches, sockets, fan installation, and appliance checks.",
        category="Electrical"
    )
    cleaning = Service(
        name="House Cleaning",
        base_price=500.0,
        time_required=120,
        description="Deep cleaning of rooms, kitchen, bathrooms, dusting, and vacuuming.",
        category="Cleaning"
    )
    ac_repair = Service(
        name="AC Servicing & Repair",
        base_price=350.0,
        time_required=90,
        description="Air conditioner cleaning, gas refilling, and general troubleshooting.",
        category="Appliances"
    )
    
    db.session.add_all([plumbing, electrical, cleaning, ac_repair])
    # Flush to get IDs
    db.session.flush()

    print("Adding customers...")
    alice = User(
        username="alice",
        email="alice@example.com",
        role="customer",
        name="Alice Smith",
        phone="1234567890",
        address="123 Maple St, Sector 4",
        pin_code="110001",
        is_active=True,
        is_approved=True
    )
    alice.set_password("password")

    bob = User(
        username="bob",
        email="bob@example.com",
        role="customer",
        name="Bob Jones",
        phone="9876543210",
        address="456 Oak Rd, Sector 12",
        pin_code="110002",
        is_active=True,
        is_approved=True
    )
    bob.set_password("password")

    charlie = User(
        username="charlie",
        email="charlie@example.com",
        role="customer",
        name="Charlie Brown",
        phone="5551234567",
        address="789 Pine Ave, Sector 8",
        pin_code="110003",
        is_active=True,
        is_approved=True
    )
    charlie.set_password("password")

    db.session.add_all([alice, bob, charlie])
    db.session.flush()

    print("Adding professionals...")
    dave = User(
        username="dave",
        email="dave@example.com",
        role="professional",
        name="Dave Miller",
        phone="1112223333",
        address="321 Cedar Ln, Sector 4",
        pin_code="110001",
        service_type_id=plumbing.id,
        experience=5,
        description="Experienced plumber with 5 years of experience in residential work.",
        is_active=True,
        is_approved=True # Dave is pre-approved
    )
    dave.set_password("password")

    eve = User(
        username="eve",
        email="eve@example.com",
        role="professional",
        name="Eve Davis",
        phone="4445556666",
        address="654 Birch Rd, Sector 12",
        pin_code="110002",
        service_type_id=electrical.id,
        experience=8,
        description="Licensed electrician specializing in household lighting and wiring.",
        is_active=True,
        is_approved=True # Eve is pre-approved
    )
    eve.set_password("password")

    frank = User(
        username="frank",
        email="frank@example.com",
        role="professional",
        name="Frank Wilson",
        phone="7778889999",
        address="98 Elm St, Sector 8",
        pin_code="110003",
        service_type_id=cleaning.id,
        experience=3,
        description="Professional home cleaning specialist with focus on sanitization.",
        is_active=True,
        is_approved=False # Frank is PENDING approval!
    )
    frank.set_password("password")

    db.session.add_all([dave, eve, frank])
    db.session.flush()

    print("Adding service requests...")
    # 1. Closed request (Alice requested Plumbing, Dave completed it, Alice reviewed it)
    sr1 = ServiceRequest(
        service_id=plumbing.id,
        customer_id=alice.id,
        professional_id=dave.id,
        date_of_request=datetime.utcnow() - timedelta(days=2),
        preferred_date=datetime.utcnow() - timedelta(days=1),
        date_of_completion=datetime.utcnow() - timedelta(days=1),
        service_status="closed",
        remarks="Leaky tap in guest bathroom",
        customer_address=alice.address,
        customer_pin_code=alice.pin_code
    )
    db.session.add(sr1)
    db.session.flush()

    # Create review for sr1
    review1 = Review(
        service_request_id=sr1.id,
        customer_id=alice.id,
        professional_id=dave.id,
        rating=5,
        comment="Dave was fast, professional, and fixed the leak perfectly!"
    )
    db.session.add(review1)

    # 2. Assigned request (Bob requested Electrical, Eve accepted it, request is active)
    sr2 = ServiceRequest(
        service_id=electrical.id,
        customer_id=bob.id,
        professional_id=eve.id,
        date_of_request=datetime.utcnow() - timedelta(hours=12),
        preferred_date=datetime.utcnow() + timedelta(days=1),
        service_status="assigned",
        remarks="Wall socket sparking in bedroom",
        customer_address=bob.address,
        customer_pin_code=bob.pin_code
    )
    db.session.add(sr2)

    # 3. Requested request (Charlie requested Plumbing, not yet accepted)
    sr3 = ServiceRequest(
        service_id=plumbing.id,
        customer_id=charlie.id,
        date_of_request=datetime.utcnow() - timedelta(hours=2),
        preferred_date=datetime.utcnow() + timedelta(days=2),
        service_status="requested",
        remarks="Kitchen sink drainage is extremely slow",
        customer_address=charlie.address,
        customer_pin_code=charlie.pin_code
    )
    db.session.add(sr3)

    db.session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
