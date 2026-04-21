# 🏥 HMIS — Health Management Information System

A full-stack Health Management Information System built with **Django REST Framework** (backend) and **Angular** (frontend).

---

## 📁 Project Structure

```
hmis/
├── backend/                        # Django Project
│   ├── manage.py
│   ├── requirements.txt
│   ├── hmis_project/               # Django project config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── core/                       # Core Django application
│       ├── migrations/
│       ├── models/
│       │   ├── __init__.py
│       │   ├── patient.py          # Patient demographics & records
│       │   ├── doctor.py           # Doctor / staff profiles
│       │   ├── appointment.py      # Appointment scheduling
│       │   ├── medical_record.py   # Diagnoses, notes, vitals
│       │   ├── prescription.py     # Medications & dosages
│       │   └── billing.py          # Invoices & payments
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── admin.py
│
└── frontend/                       # Angular Project
    ├── angular.json
    ├── package.json
    └── src/
        ├── app/
        │   ├── core/               # Auth guards, interceptors, services
        │   ├── shared/             # Reusable components & pipes
        │   └── modules/
        │       ├── dashboard/      # Overview & statistics
        │       ├── patients/       # Patient CRUD & search
        │       ├── appointments/   # Calendar & scheduling
        │       ├── medical-records/# View & create records
        │       ├── prescriptions/  # Medication management
        │       └── billing/        # Invoice & payment tracking
        ├── assets/
        └── environments/
```

---

## 🗄️ Core Models (Django)

| Model | Description |
|---|---|
| `Patient` | Personal info, blood type, allergies, registration date |
| `Doctor` | Staff profile, specialisation, license number |
| `Appointment` | Links patient ↔ doctor, date/time, status, reason |
| `MedicalRecord` | Diagnosis, symptoms, vitals (BP, weight, temp), notes |
| `Prescription` | Medication name, dosage, frequency, linked to record |
| `Billing` | Invoice per visit, itemised costs, payment status |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Django 4.x + Django REST Framework |
| Database | PostgreSQL (dev: SQLite) |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Frontend | Angular 17+ (standalone components) |
| HTTP Client | Angular `HttpClient` with interceptors |
| UI Library | Angular Material |
| State | Angular Services + RxJS |

---

## 🚀 Getting Started

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
ng serve                            # http://localhost:4200
```

### API Base URL
```
http://localhost:8000/api/
```

---

## 🔑 Key API Endpoints

```
POST   /api/auth/login/
POST   /api/auth/refresh/

GET    /api/patients/
POST   /api/patients/
GET    /api/patients/{id}/

GET    /api/appointments/
POST   /api/appointments/
PATCH  /api/appointments/{id}/

GET    /api/medical-records/
POST   /api/medical-records/

GET    /api/prescriptions/
POST   /api/prescriptions/

GET    /api/billing/
POST   /api/billing/
```

---

## 👥 Roles

- **Admin** — Full system access
- **Doctor** — View/create records, prescriptions, appointments
- **Receptionist** — Manage patients, appointments, billing

---

*Built for efficient, paper-free healthcare operations.*