# CampusPulse — Full-Stack Student Portal

A responsive, campus-energy full-stack web application designed for students, faculty, and academic administrators. Built with a **Django backend** and a decoupled, semantic **frontend module** featuring a curated campus design system.

---

## Architecture & Design Decisions

- **Architecture Choice (Option A — Django Templates):**
  - Django server-side renders semantic HTML5 templates using clean template inheritance (`base.html`).
  - Session-based authentication with cryptographic password hashing via Django's auth system.
  - Complete separation between `backend/` (project settings, apps: `accounts`, `academics`, `dashboard`) and `frontend/` (`templates/`, `static/css/`, `static/js/`, `static/images/`).
- **Design System & Palette:**
  - **Base Background:** Pale mist blue (`#F4F7FB`)
  - **Surface:** White (`#FFFFFF`)
  - **Primary (brand):** Deep indigo-plum (`#3D2C7A`)
  - **Primary Hover:** Darker plum (`#2C1F5C`)
  - **Accent — Courses:** Marigold (`#F5A623`) for chips, badges, and hero accent
  - **Accent — Success / Attendance:** Teal-mint (`#1FB6A6`) for attendance $\ge 75\%$ ("Good Standing")
  - **Accent — Alerts:** Coral (`#FF6B5E`) for attendance $< 75\%$ ("Attendance Alert") and inline form errors
  - **Text:** Near-charcoal (`#232336`) body and slate grey (`#6B7280`) muted
- **Typography:**
  - **Headings & Display:** `Fraunces` (expressive, warm serif)
  - **Body & UI:** `Work Sans` (clean geometric sans)
  - Real typographic scale (`2.75rem` hero &rarr; `2rem` section &rarr; `1.25rem` card &rarr; `1rem` body &rarr; `0.875rem` small) without pseudo-bold hacks or all-caps styling.
- **Client-Side Validation (`validation.js`):**
  - Instantaneous feedback on blur and submit.
  - Required fields, RFC-compliant email checking, password length ($\ge 8$ characters), and password match confirmation.
  - Inline error messages in coral (`#FF6B5E`), preventing submission until valid.

---

## Project Structure

```text
exam/
├── .env.example                   # Environment configuration template
├── .env                           # Local environment variables (loaded via python-dotenv)
├── requirements.txt               # Pinned Python dependencies
├── README.md                      # Comprehensive documentation
│
├── frontend/                      # Decoupled Frontend Module
│   ├── templates/                 # Semantic HTML5 templates
│   │   ├── base.html              # Base shell with Google Fonts & design tokens
│   │   ├── landing.html           # Landing page (Hero, About, Features, Courses, Contact, Dark Footer)
│   │   ├── accounts/
│   │   │   ├── login.html         # Centered card login (max-width ~420px) with brand badge
│   │   │   ├── register.html      # Centered card registration with student profile fields
│   │   │   └── profile_edit.html  # Student profile & avatar editor
│   │   ├── academics/
│   │   │   ├── course_list.html   # Campus course catalog
│   │   │   └── course_detail.html # Course syllabus & student session attendance breakdown
│   │   └── dashboard/
│   │       └── dashboard.html     # Sidebar navigation, profile card, course chips, attendance badges
│   └── static/
│       ├── css/
│       │   ├── base.css           # CSS custom properties, tokens, typography, utilities
│       │   ├── landing.css        # Hero 2-col layout, feature grid, contact, footer
│       │   ├── auth.css           # Centered card auth styles and focus states
│       │   └── dashboard.css      # Indigo-plum sidebar, stat cards, progress bars, responsive drawer
│       ├── js/
│       │   ├── validation.js      # Real-time inline form validation
│       │   └── dashboard.js       # Mobile drawer toggle, tab scrolling, alert dismiss
│       └── images/
│
└── backend/                       # Django Backend Module
    ├── manage.py
    ├── studentportal/             # Core project configuration
    │   ├── settings.py            # Reads .env, loads frontend templates and static files
    │   ├── urls.py                # Root routing
    │   ├── views.py               # Landing page view
    │   ├── wsgi.py
    │   └── asgi.py
    ├── accounts/                  # Student Profiles & Authentication
    │   ├── models.py              # Student model (OneToOne User, roll number, department, bio)
    │   ├── forms.py               # RegistrationForm, LoginForm, StudentProfileUpdateForm
    │   ├── views.py               # register_view, login_view, logout_view, profile_update_view
    │   ├── admin.py               # Django Admin integration for Students
    │   └── urls.py
    ├── academics/                 # Courses, Enrollments & Attendance
    │   ├── models.py              # Course, Enrollment, Attendance models with unique constraints
    │   ├── views.py               # course_list, course_detail, course_enroll, course_drop
    │   ├── admin.py               # Admin displays with inlines, filters, search
    │   ├── management/commands/
    │   │   └── seed_data.py       # Populates realistic demo students, courses & attendance
    │   └── urls.py
    └── dashboard/                 # Student Portal Analytics
        ├── views.py               # dashboard_view calculates attendance %, standing, credits
        └── urls.py
```

---

## Data Models (ORM)

1. **`Student` (`accounts.models`):**
   - Linked `OneToOne` with Django `User`.
   - Fields: `roll_number` (unique), `phone`, `department`, `date_of_birth`, `profile_photo`, `bio`.
   - Properties: `full_name`, `initials`, `email`.
2. **`Course` (`academics.models`):**
   - Fields: `code` (unique, e.g. `CS101`), `name`, `description`, `credits`, `instructor`, `department`, `is_active`.
   - Methods: `total_students`.
3. **`Enrollment` (`academics.models`):**
   - Links `Student` &harr; `Course`.
   - Fields: `enrollment_date`, `status` (`active`, `completed`, `dropped`).
   - `unique_together = ('student', 'course')` prevents duplicate enrollments.
4. **`Attendance` (`academics.models`):**
   - Links `Student` &harr; `Course` &harr; `Date`.
   - Fields: `date`, `status` (`present`, `absent`, `late`), `remarks`.
   - `unique_together = ('student', 'course', 'date')`.

---

## Quickstart & Installation

### 1. Prerequisites
- Python 3.11+ (Python 3.14 compatible)

### 2. Create and Activate Virtual Environment
```bash
# In the repository root
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
cd backend
python manage.py migrate
```

### 5. Seed Demo Data (Students, Courses, Attendance)
```bash
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

Open your browser and visit:
- **Landing Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Student Sign In:** [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
- **Student Registration:** [http://127.0.0.1:8000/accounts/register/](http://127.0.0.1:8000/accounts/register/)
- **Password Reset:** [http://127.0.0.1:8000/accounts/password-reset/](http://127.0.0.1:8000/accounts/password-reset/)
- **Faculty & Staff Portal:** [http://127.0.0.1:8000/accounts/staff-login/](http://127.0.0.1:8000/accounts/staff-login/)
- **Student Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- **Django Admin Console:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Seed Accounts & Environment Credentials

The `seed_data` command reads bootstrap account credentials from your `.env` configuration (default template provided in `.env.example`):

| Role | Username | Password Setting | Notes |
|---|---|---|---|
| **Student** | `alex_morgan` | `STUDENT_PASSWORD` in `.env` | Roll No: `STU-2026-0042`. Enrolled in 4 courses. Demonstrates good standing (teal), alert standing (coral), and neutral states. |
| **Student** | `jordan_lee` | `STUDENT_PASSWORD` in `.env` | Roll No: `STU-2026-0089`. Data Science major. |
| **Student** | `priya_sharma` | `STUDENT_PASSWORD` in `.env` | Roll No: `STU-2026-0115`. Information Tech major. |
| **Staff / Admin** | `admin` | `ADMIN_PASSWORD` in `.env` | Full access to Faculty & Staff Portal and Django Admin. |

> [!NOTE]
> Demo credential shortcut boxes in the user interface are strictly gated behind `{% if debug %}` and never render in production environments (`DEBUG=False`).

---

## Password Recovery (Email Backend)

In development mode, Django uses the console email backend:
- `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
- When a student requests a password reset from `/accounts/password-reset/`, the generated reset token link prints directly to the terminal running `python manage.py runserver`.

---

## Security & Data Mutation (POST Only)

- Course enrollment (`/academics/courses/<id>/enroll/`) and course dropping (`/academics/courses/<id>/drop/`) require **POST** requests protected with Django CSRF tokens (`@require_POST`).
- Course drop actions trigger an explicit confirmation step before form submission.

---

## Attendance Calculation & Neutral States

- When a student is enrolled in a course with **zero recorded sessions**, the interface displays an honest, neutral slate-grey badge (`No sessions yet`), avoiding deceptive 100% standing calculations.
- Courses with recorded sessions apply the functional color rules: **Teal-Mint** for $\ge 75\%$ ("Good Standing") and **Coral** for $< 75\%$ ("Attendance Alert").

---

## Running Automated Tests

A comprehensive test suite covers authentication, staff permissions, password reset, unique constraints, POST enroll/drop mutations, and zero-session edge cases.

Run tests from the `backend/` directory:
```bash
cd backend
python manage.py test
```

---

## Production & PostgreSQL Readiness

The project is structured to seamlessly switch from SQLite to PostgreSQL:
- Set `DATABASE_URL=postgresql://user:password@host:5432/dbname` in `.env`.
- `settings.py` automatically detects PostgreSQL connections.
- Set `DEBUG=False` and supply a strong `SECRET_KEY` in production.
