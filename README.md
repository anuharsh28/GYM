# ACEest Fitness & Gym — DevOps CI/CD Pipeline

## Project Overview
A Flask-based REST API for gym client and program management,
built as the web-service backend of the ACEest Fitness desktop application.
Implements a full automated CI/CD pipeline using GitHub Actions and Jenkins.

**Course:** Introduction to DevOps (CSIZG514/SEZG514/SEUSZG514)

---

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python 3.11 + Flask | REST API web application |
| SQLite | Lightweight database for client data |
| Pytest | Automated unit testing (30+ tests) |
| Docker | Containerization & environment consistency |
| GitHub Actions | Automated CI/CD pipeline |
| Jenkins | Build server / secondary quality gate |

---

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and endpoint list |
| GET | `/health` | Service health check |
| GET | `/programs` | All available training programs |
| GET | `/members` | All gym members |
| POST | `/members` | Add a new member |
| GET | `/classes` | Gym class schedule |
| GET | `/equipment` | Available equipment |
| GET | `/calories?weight=70&program=Beginner` | Calorie calculator |

---

## Local Setup

### Prerequisites
- Python 3.8+
- Docker Desktop

### Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/aceest-gym.git
cd aceest-gym
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

### Run Tests Manually
```bash
pytest test_app.py -v
```

---

## Docker Setup
```bash
# Build image
docker build -t aceest-gym .

# Run container
docker run -p 5000:5000 aceest-gym

# Run tests inside container
docker run aceest-gym pytest test_app.py -v
```

---

## GitHub Actions Pipeline
Every push to `main` automatically triggers:
1. **Checkout** — Downloads latest code
2. **Lint** — `flake8` checks for syntax errors
3. **Docker Build** — Builds the container image
4. **Test** — Runs full pytest suite inside the container

Pipeline config: `.github/workflows/main.yml`

---

## Jenkins Integration
Jenkins pulls the latest code from GitHub and runs a clean build in a
controlled environment, serving as a secondary validation layer.

**Build steps:**
1. `pip install -r requirements.txt`
2. `flake8 app.py --max-line-length=100`
3. `pytest test_app.py -v`

---

## Project Structure
```
aceest-gym/
├── app.py                    # Flask REST API application
├── test_app.py               # Pytest test suite (30+ tests)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── README.md                 # This file
└── .github/
    └── workflows/
        └── main.yml          # GitHub Actions CI/CD pipeline
```
