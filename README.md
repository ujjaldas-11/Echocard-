# ⚡ EchoCard — AI-Powered Flashcard & Notes Generator

> Generate flashcards and study notes from text or PDF using Groq AI (llama-3.3-70b-versatile)

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0.3-green?style=flat-square&logo=django)](https://djangoproject.com)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)
[![Live](https://img.shields.io/badge/Live-echocard.onrender.com-brightgreen?style=flat-square)](https://echocard.onrender.com)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running the App](#-running-the-app)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🃏 **Flashcard Generation** | Generate flashcards from text or PDF |
| 📝 **Notes Generation** | Generate summaries and key points |
| 🤖 **AI Powered** | Uses Groq llama-3.3-70b-versatile |
| 📄 **PDF Support** | Extract text from PDF files |
| 🔐 **Authentication** | Web login/register + JWT API auth |
| 🔍 **Search** | Search decks and notes |
| 🌐 **REST API** | Full API with Swagger UI |
| 👤 **Multi-user** | Each user owns their own data |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0.3 |
| **AI** | Groq API (llama-3.3-70b-versatile) |
| **PDF** | pdfplumber |
| **API** | Django Ninja + Django Ninja Extra |
| **Auth** | Django Ninja JWT |
| **Database** | PostgreSQL |
| **Static Files** | Whitenoise |
| **Server** | Gunicorn |
| **Frontend** | Bootstrap 5 (dark theme) |

---

## 📁 Project Structure

```
EchoCard/
└── echocard/
    ├── echocard/               ← Django project settings
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── api.py              ← Django Ninja API
    ├── flashcards/             ← Main app
    │   ├── models.py           ← Deck, Flashcard, Note
    │   ├── views.py            ← Web views
    │   ├── auth_views.py       ← Login, Register, Logout
    │   ├── urls.py
    │   ├── forms.py
    │   └── ai_service.py       ← Groq AI + PDF extraction
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── create_flashcards.html
    │   ├── view_deck.html
    │   ├── create_notes.html
    │   ├── view_note.html
    │   └── auth/
    │       ├── login.html
    │       └── register.html
    ├── static/
    ├── manage.py
    ├── requirements.txt
    ├── Procfile
    ├── runtime.txt
    └── .env
```

---

## ✅ Prerequisites

- Python 3.12+
- PostgreSQL
- Groq API key → [Get one free at console.groq.com](https://console.groq.com)
- Git

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/EchoCard.git
cd EchoCard/
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 4. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# PostgreSQL
DB_NAME=echocard
DB_USER=echocard_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

> 💡 Generate a secret key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🗄️ Database Setup

### 5. Create PostgreSQL database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE echocard;
CREATE USER echocard_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE echocard TO echocard_user;
ALTER DATABASE echocard OWNER TO echocard_user;
\q
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create superuser (optional)

```bash
python manage.py createsuperuser
```

---

## ▶️ Running the App

### 8. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 9. Start development server

```bash
python manage.py runserver
```

Visit:

| URL | Description |
|---|---|
| `http://localhost:8000/` | Home |
| `http://localhost:8000/register/` | Register |
| `http://localhost:8000/login/` | Login |
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/admin/` | Django Admin |

---

## 📡 API Documentation

The REST API is built with Django Ninja and supports JWT authentication.

### Authentication

```bash
# Register
POST /api/auth/register

# Login (get token)
POST /api/token/pair

# Get current user
GET /api/auth/me
```

### Flashcards

```bash
# Generate from text
POST /api/decks/generate/text

# Generate from PDF
POST /api/decks/generate/pdf

# List all decks
GET /api/decks

# Get deck detail
GET /api/decks/{id}

# Delete deck
DELETE /api/decks/{id}
```

### Notes

```bash
# Generate from text
POST /api/notes/generate/text

# Generate from PDF
POST /api/notes/generate/pdf

# List all notes
GET /api/notes

# Get note detail
GET /api/notes/{id}

# Delete note
DELETE /api/notes/{id}
```

> 📖 Full interactive docs at `/api/docs`

---

## 🌐 Deployment

### Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Web Service → Connect GitHub repo
4. Configure:

```
Build Command:   pip install -r requirements.txt && python manage.py collectstatic --noinput
Start Command:   gunicorn echocard.wsgi:application --bind 0.0.0.0:$PORT
Pre-Deploy:      python manage.py migrate
```

5. Add environment variables:

```
SECRET_KEY, DEBUG=False, GROQ_API_KEY, GROQ_MODEL, DATABASE_URL
```

6. Add PostgreSQL service and link `DATABASE_URL`

### Live Demo

🌐 **[https://echocard.onrender.com](https://echocard.onrender.com)**

---

## 📸 Screenshots

| Page | Description |
|---|---|
| `/` | Home — view all decks and notes |
| `/flashcards/create/` | Create flashcards from text or PDF |
| `/notes/create/` | Generate notes from text or PDF |
| `/api/docs` | Interactive Swagger API docs |

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Ujjal Das**
- GitHub: [@ujjaldas](https://github.com/ujjaldas)
- Live: [echocard.onrender.com](https://echocard.onrender.com)

---

<p align="center">Made with ❤️ and ⚡ Groq AI</p>
