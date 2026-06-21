# 🛠️ SkillFleet — Modern Household Services Platform

[![Live Demo](https://img.shields.io/badge/Demo-Live%20on%20Render-brightgreen.svg)](https://skill-fleet.onrender.com/login)

**SkillFleet** is a comprehensive, three-role marketplace platform designed to bridge the gap between service customers and professional household service providers (e.g. plumbers, cleaners, technicians). Built as a high-fidelity SaaS web application, it offers interactive workflows, custom admin stats, live chat simulations, and a fully responsive interface.

🔗 **Live Link**: [https://skill-fleet.onrender.com/login](https://skill-fleet.onrender.com/login)

---

## 🌟 Key Features

*   👥 **Three-Role Ecosystem**: Tailored dashboards for **Customers**, **Service Professionals**, and **Administrators** with role-based routing and access control.
*   🌓 **Zero-Flash Dark Mode**: A unified theme-toggling system persisting user preference in `localStorage`, using an early head-loading script to prevent blinding white flashes.
*   🔧 **Dynamic Services Catalog**: Administrators can execute full CRUD operations (Create, Read, Update, Delete) on home services, categorizing them dynamically with custom indicators.
*   💬 **Simulated Coordinator Chat**: Real-time communication simulation modal on both customer and professional dashboards, facilitating messaging and coordination.
*   📊 **Interactive Chart.js Dashboard**: Administrative analytics rendering pie charts for request status splits and bar charts for category booking volume, updating colors on theme toggles.
*   ⭐ **Interactive Star Reviews**: Interactive, CSS-driven click-to-rate star panels replacing raw text dropdown fields during service closing review steps.
*   🗓️ **Airbnb-Style Checkout Layout**: Split-screen checkout forms validating date selections client-side to block past bookings, displaying dynamic pricing calculations.

---

## 📸 Screenshots

| Page / Dashboard | Visual Preview (Insert Your Images Below) |
|---|---|
| **Split Login Screen** | *[Insert `/static/screenshots/login.png`]* |
| **Customer Dashboard** | *[Insert `/static/screenshots/customer_dashboard.png`]* |
| **Admin Stats & Charts** | *[Insert `/static/screenshots/admin_dashboard.png`]* |
| **Interactive Star Reviews** | *[Insert `/static/screenshots/star_ratings.png`]* |
| **Coordinator Chat Simulation** | *[Insert `/static/screenshots/chat_simulator.png`]* |

---

## 💻 Tech Stack

### Backend
*   **Language**: Python 3.10+
*   **Web Framework**: Flask (WSGI Web Server)
*   **Database ORM**: Flask-SQLAlchemy (SQLAlchemy Core)
*   **Authentication & Sessions**: Flask-Login
*   **Form Validation**: WTForms (with CSRF protection via Flask-WTF)
*   **Security**: Werkzeug Security Hash Algorithms

### Frontend
*   **Styling**: Custom CSS3 Variables + Bootstrap 5.3
*   **Icons**: Bootstrap Icons Pack
*   **Charts Engine**: Chart.js v4.4
*   **Interactions**: Vanilla JavaScript ES6

### Database
*   **Dev Engine**: SQLite (`instance/skillfleet.db`)

---

## 📂 Project Structure

```text
HSA/
├── app.py                  # App entry point, config, Blueprint registrations
├── models.py               # SQLAlchemy Database Models (User, Service, ServiceRequest, Review)
├── forms.py                # WTForms validation schemas (Login, Register, Booking, Reviews)
├── api.py                  # API endpoints returning JSON statistics and listings
├── seed_test_data.py       # Local automation script to seed test users and mock data
├── routes/                 # Role-based Route Controller Layers
│   ├── auth.py             # User Register / Login / Logout flows
│   ├── admin.py            # Service Management and Admin Dashboard
│   ├── customer.py         # Search, Booking, requests overview, and review submittals
│   └── professional.py     # Accept, Reject, Complete bookings overview
├── static/
│   ├── css/
│   │   └── style.css       # Unified light/dark theme variables, animations, custom selectors
│   └── js/
│       └── charts.js       # Dynamic theme-aware Chart.js dashboard loading scripts
├── templates/
│   ├── base.html           # Main base template containing navigation, alert handlers & loader
│   ├── admin/              # Admin-facing layouts (dashboard, service grids, user lists)
│   ├── auth/               # Login & Register SaaS split layouts
│   ├── customer/           # Booking checkers, reviews, and client logs
│   ├── professional/       # Job requests lists, profile details, and coordinate buttons
│   └── errors/             # Custom Error Layout Panels (403, 404, 500)
└── requirements.txt        # Project dependency listings
```

---

## ⚙️ Installation

To set up and run SkillFleet locally:

### 1. Clone the Repository
```bash
git clone https://github.com/grv931/Skill-Fleet.git
cd Skill-Fleet
```

### 2. Configure Virtual Environment
Create and activate a Python virtual environment:
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
.\venv\Scripts\activate.bat

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed Development Database
Optionally populate the database with mock services, customers, and professionals:
```bash
python seed_test_data.py
```

---

## 🔑 Usage

Start the Flask development server:
```bash
python app.py
```
By default, the application will run at **`http://127.0.0.1:5000`**.

### Default Credentials
If you populated the database using `seed_test_data.py`, use the following credentials to sign in:

| Role | Email Address | Password |
|---|---|---|
| **Administrator** | `admin@skillfleet.com` | `admin123` |
| **Customer** | `alice@example.com` | `password` |
| **Professional** | `charlie@example.com` | `password` |

---

## 🛡️ User Roles & Permissions

| Feature | Customer | Professional | Admin |
|---|:---:|:---:|:---:|
| **Browse / Search Services** | Yes | No | Yes |
| **Book Service Requests** | Yes | No | No |
| **Rate & Review Closed Jobs** | Yes | No | No |
| **Accept / Complete Assigned Bookings** | No | Yes | No |
| **Manage Profile Credentials** | Yes | Yes | Yes |
| **Approve / Block User Accounts** | No | No | Yes |
| **Create / Edit / Delete Services** | No | No | Yes |
| **View Analytics Charts** | No | No | Yes |

---

## 🔮 Future Roadmap

*   🚀 **Production Deployment**: Completed initial production release on Render. Live at [https://skill-fleet.onrender.com/login](https://skill-fleet.onrender.com/login).
*   🔗 **Live Stripe Connect Integration**: Enable actual billing transactions, handling escrow locks, and release of professional payouts upon completion.
*   📍 **Geofenced Search (Geo-Proximity)**: Match customers with professionals based on live coordinates using OpenStreetMap integration.
*   📊 **Exportable Analytics Reports**: Allow administrators to export PDF/CSV files of monthly billing audits, request lists, and reviews.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the project repository.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

*   **grv931** - [GitHub Profile](https://github.com/grv931)
*   Project Repository: [https://github.com/grv931/Skill-Fleet](https://github.com/grv931/Skill-Fleet)