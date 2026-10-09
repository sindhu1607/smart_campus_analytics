# Smart Campus Analytics — AI-Powered Student Success Platform

An institutional analytics and machine learning platform built with **Django 5/6**, **Django REST Framework**, and **Pandas/NumPy**. It unifies academic records, attendance logs, LMS activity, extracurricular engagement, placement readiness, skills assessments, and student feedback into an actionable, explainable intelligence platform.

---

## 🗺️ Four-Part Roadmap Overview

- **Part 1 (Completed): Project Foundation & Database**  
  Django architecture, custom role-based authentication, normalized database schema across 10+ campus domains, admin configuration, synthetic data generation, CSV/Excel import pipelines, and base UI.
- **Part 2 (Completed): Analytics & AI Engine**  
  Explainable Student Success Scoring, academic/attendance risk prediction algorithms, placement readiness scoring, automated intervention generation, and REST APIs.
- **Part 3: Frontend & Dynamic Analytics Dashboards**  
  Interactive role-based dashboards (Admin, Faculty, Placement Officer, Student), visual risk indicators, and intervention workflow UI.
- **Part 4: Closed-Loop Integration & Finalization**  
  Full end-to-end integration, automated testing, system validation, and demonstration readiness.

---

## 🛠️ Technology Stack

- **Backend Framework:** Python 3.12+ / 3.14, Django 5.x/6.x, Django ORM
- **REST APIs:** Django REST Framework (DRF)
- **Data Science & Processing:** Pandas, NumPy, Matplotlib, SciPy
- **Database:** SQLite (Local Dev Fallback) / PostgreSQL (Production ready via `dj-database-url`)
- **Frontend Stack:** Django Templates, Bootstrap 5, HTML5, CSS3, JavaScript, Chart.js CDN ready
- **Testing & Tooling:** Django Test Framework, Pytest, python-dotenv, openpyxl, django-filter

---

## 📁 Directory Structure

```
smart_campus_analytics/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── README.md
├── sample_student_import_template.csv
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/         # Custom User Model & Role Permissions
│   ├── students/         # Department, Program, StudentProfile & Import Services
│   ├── academics/        # Subjects, Semester & Assessment Results
│   ├── attendance/       # Attendance Tracking & Enforced Validation
│   ├── lms/              # LMS Activity & Assignment Timeliness Metrics
│   ├── engagement/       # Clubs, Hackathons & Extracurriculars
│   ├── placements/       # Aptitude, Coding & Application Readiness
│   ├── skills/           # Technical & Soft Skill Assessments
│   ├── feedback/         # Confidential Feedback & Faculty Notes
│   ├── analytics/        # Student Success Snapshot & AI Models (Part 2 ready)
│   └── interventions/    # Closed-loop Intervention Records & Counseling Actions
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── 403.html
│   ├── 404.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── profile.html
│   └── dashboards/
│       ├── admin_dashboard.html
│       ├── faculty_dashboard.html
│       ├── placement_dashboard.html
│       └── student_dashboard.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── media/
└── tests/
    ├── __init__.py
    └── test_foundation.py
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed
- `pip` package manager

### 2. Environment Setup
Navigate to the project root:
```bash
cd smart_campus_analytics
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Migration
Apply migrations to initialize all normalized database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Synthetic Data Generation
Generate realistic demonstration data for 40+ students across departments:
```bash
python manage.py generate_sample_data --count 40
```
This automatically creates default test accounts:
- **Administrator:** `admin` / `Admin@1234`
- **Faculty:** `faculty_cse` / `Faculty@1234`
- **Placement Officer:** `placement_officer` / `Placement@1234`
- **Student:** `stu2025001` / `Student@1234`

### 5. Execute AI Analytics & Risk Engine
Recalculate explainable success scores, risk levels, and automated interventions for all active students:
```bash
python manage.py run_analytics_engine
```

### 6. CSV/Excel Dataset Import
To import custom datasets:
```bash
python manage.py import_student_data sample_student_import_template.csv
```

### 7. Run System Test Suite
Execute the full foundation and AI analytics test suite (12 tests):
```bash
python manage.py test tests
```

### 7. Start Development Server
```bash
python manage.py runserver 8000
```
Open your browser and visit: `http://127.0.0.1:8000/`
