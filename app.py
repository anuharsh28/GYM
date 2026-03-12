"""
ACEest Fitness & Gym - Flask Web Application
Version: 1.0.0 (DevOps Assignment Edition)
Description: REST API for gym client and program management
Based on the ACEest desktop application (v1.0 through v3.1.2)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_NAME = os.environ.get("DB_NAME", "aceest_fitness.db")

# ── Programs data (from the original desktop app) ──────────────────────────
PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "desc": "3-day full-body fat loss program",
        "workout": "Mon: 5x5 Back Squat + AMRAP, Wed: EMOM 20min Cardio, Fri: Bench + Deadlift",
        "diet": "Egg Whites, Grilled Chicken, Fish Curry, Brown Rice",
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "desc": "5-day split, higher volume fat loss",
        "workout": "Mon-Fri split: Upper/Lower/Push/Pull/Full",
        "diet": "High protein, low carb Tamil meals",
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy program",
        "workout": "Squat, Bench, Deadlift, Press, Rows - 6 days",
        "diet": "Eggs, Chicken Biryani, Mutton Curry, 3200 kcal",
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "3-day simple beginner full-body",
        "workout": "Air Squats, Ring Rows, Push-ups - technique focus",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal",
    },
}


# ── Database helpers ────────────────────────────────────────────────────────
def get_db():
    db = app.config.get("DB_NAME", DB_NAME)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_expiry TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT,
            adherence INTEGER,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


# Initialize DB on startup
init_db()


# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Home route - welcome message and API overview"""
    return jsonify({
        "app": "ACEest Fitness & Gym",
        "version": "1.0.0",
        "status": "running",
        "message": "Welcome to ACEest Fitness & Gym API!",
        "endpoints": ["/health", "/programs", "/members", "/classes", "/equipment", "/calories"]
    })


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "aceest-gym",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/programs")
def get_programs():
    """Return all available training programs"""
    return jsonify({
        "total": len(PROGRAMS),
        "programs": [
            {
                "name": name,
                "description": data["desc"],
                "calorie_factor": data["factor"],
                "workout_summary": data["workout"],
                "diet_summary": data["diet"],
            }
            for name, data in PROGRAMS.items()
        ],
    })


@app.route("/members")
def members():
    """Return all gym members from the database"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, age, weight, program, membership_expiry FROM clients ORDER BY name"
    )
    rows = cur.fetchall()
    conn.close()

    members_list = [
        {
            "id": row["id"],
            "name": row["name"],
            "age": row["age"],
            "weight": row["weight"],
            "program": row["program"],
            "membership_expiry": row["membership_expiry"],
        }
        for row in rows
    ]
    return jsonify({"total": len(members_list), "members": members_list})


@app.route("/members", methods=["POST"])
def add_member():
    """Add a new gym member"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    program = data.get("program", "")
    weight = data.get("weight", 0)
    factor = PROGRAMS.get(program, {}).get("factor", 25)
    calories = int(weight * factor) if weight > 0 else None

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO clients (name, age, height, weight, program, calories, membership_expiry)
               VALUES (?,?,?,?,?,?,?)""",
            (
                name,
                data.get("age"),
                data.get("height"),
                weight,
                program,
                calories,
                data.get("membership_expiry"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"message": f"Member '{name}' added", "id": new_id, "calories": calories}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Member '{name}' already exists"}), 409


@app.route("/classes")
def classes():
    """Return gym class schedule"""
    class_schedule = [
        {"name": "Yoga", "time": "7:00 AM", "days": "Mon/Wed/Fri", "trainer": "Priya", "capacity": 20},
        {"name": "Zumba", "time": "6:00 PM", "days": "Tue/Thu", "trainer": "Raj", "capacity": 25},
        {"name": "CrossFit", "time": "8:00 AM", "days": "Mon/Wed/Fri", "trainer": "Mike", "capacity": 15},
        {"name": "Strength Training", "time": "9:00 AM", "days": "Daily", "trainer": "Coach", "capacity": 10},
    ]
    return jsonify({"total": len(class_schedule), "classes": class_schedule})


@app.route("/equipment")
def equipment():
    """Return available gym equipment"""
    equipment_list = [
        {"name": "Treadmill", "count": 5, "status": "available"},
        {"name": "Dumbbells", "count": 20, "status": "available"},
        {"name": "Barbell + Rack", "count": 4, "status": "available"},
        {"name": "Pull-up Bar", "count": 3, "status": "available"},
        {"name": "Rowing Machine", "count": 2, "status": "available"},
        {"name": "Assault Bike", "count": 3, "status": "available"},
    ]
    return jsonify({"total": len(equipment_list), "equipment": equipment_list})


@app.route("/calories")
def calculate_calories():
    """Calculate daily calorie target given weight and program query params"""
    weight = request.args.get("weight", type=float)
    program = request.args.get("program", "")

    if not weight:
        return jsonify({
            "error": "weight query param required",
            "example": "/calories?weight=70&program=Beginner (BG)"
        }), 400

    factor = 25
    matched_program = "Default"
    for name, data in PROGRAMS.items():
        if program.lower() in name.lower():
            factor = data["factor"]
            matched_program = name
            break

    calories = int(weight * factor)
    return jsonify({
        "weight_kg": weight,
        "program": matched_program,
        "daily_calories_kcal": calories,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
