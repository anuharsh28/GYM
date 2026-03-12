"""
ACEest Fitness & Gym - Test Suite
Tests all Flask API endpoints using pytest
"""

import pytest
import json
import os
from app import app, PROGRAMS, init_db


# ── FIXTURE: test client ────────────────────────────────────────────────────
@pytest.fixture
def client():
    """Create a Flask test client with a fresh test database"""
    app.config["TESTING"] = True
    app.config["DB_NAME"] = "test_aceest.db"
    init_db()

    with app.test_client() as client:
        yield client

    if os.path.exists("test_aceest.db"):
        os.remove("test_aceest.db")


# ── HOME ROUTE ──────────────────────────────────────────────────────────────
def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_home_returns_json(client):
    response = client.get("/")
    assert response.content_type == "application/json"

def test_home_contains_app_name(client):
    data = client.get("/").get_json()
    assert "app" in data
    assert "ACEest" in data["app"]

def test_home_contains_endpoints_list(client):
    data = client.get("/").get_json()
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) > 0


# ── HEALTH CHECK ────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    assert client.get("/health").status_code == 200

def test_health_status_is_healthy(client):
    data = client.get("/health").get_json()
    assert data["status"] == "healthy"

def test_health_contains_service_name(client):
    data = client.get("/health").get_json()
    assert "service" in data
    assert data["service"] == "aceest-gym"

def test_health_contains_timestamp(client):
    data = client.get("/health").get_json()
    assert "timestamp" in data


# ── PROGRAMS ────────────────────────────────────────────────────────────────
def test_programs_returns_200(client):
    assert client.get("/programs").status_code == 200

def test_programs_returns_list(client):
    data = client.get("/programs").get_json()
    assert "programs" in data
    assert isinstance(data["programs"], list)

def test_programs_total_matches(client):
    data = client.get("/programs").get_json()
    assert data["total"] == len(PROGRAMS)
    assert data["total"] == len(data["programs"])

def test_programs_have_required_fields(client):
    data = client.get("/programs").get_json()
    for prog in data["programs"]:
        assert "name" in prog
        assert "description" in prog
        assert "calorie_factor" in prog


# ── MEMBERS ─────────────────────────────────────────────────────────────────
def test_members_returns_200(client):
    assert client.get("/members").status_code == 200

def test_members_returns_list(client):
    data = client.get("/members").get_json()
    assert "members" in data
    assert isinstance(data["members"], list)

def test_members_total_field_exists(client):
    data = client.get("/members").get_json()
    assert "total" in data

def test_add_member_returns_201(client):
    response = client.post(
        "/members",
        data=json.dumps({"name": "Test User", "age": 25, "weight": 70, "program": "Beginner (BG)"}),
        content_type="application/json",
    )
    assert response.status_code == 201

def test_add_member_returns_id(client):
    response = client.post(
        "/members",
        data=json.dumps({"name": "Alice Kumar", "age": 28, "weight": 65}),
        content_type="application/json",
    )
    data = response.get_json()
    assert "id" in data

def test_add_member_no_name_returns_400(client):
    response = client.post(
        "/members",
        data=json.dumps({"age": 25}),
        content_type="application/json",
    )
    assert response.status_code == 400

def test_add_duplicate_member_returns_409(client):
    payload = json.dumps({"name": "Bob Singh", "weight": 80})
    client.post("/members", data=payload, content_type="application/json")
    response = client.post("/members", data=payload, content_type="application/json")
    assert response.status_code == 409

def test_members_count_increases_after_add(client):
    before = client.get("/members").get_json()["total"]
    client.post(
        "/members",
        data=json.dumps({"name": "New Member", "weight": 75}),
        content_type="application/json",
    )
    after = client.get("/members").get_json()["total"]
    assert after == before + 1


# ── CLASSES ─────────────────────────────────────────────────────────────────
def test_classes_returns_200(client):
    assert client.get("/classes").status_code == 200

def test_classes_returns_list(client):
    data = client.get("/classes").get_json()
    assert "classes" in data
    assert isinstance(data["classes"], list)
    assert len(data["classes"]) > 0

def test_classes_have_required_fields(client):
    data = client.get("/classes").get_json()
    for cls in data["classes"]:
        assert "name" in cls
        assert "time" in cls
        assert "trainer" in cls


# ── EQUIPMENT ────────────────────────────────────────────────────────────────
def test_equipment_returns_200(client):
    assert client.get("/equipment").status_code == 200

def test_equipment_returns_list(client):
    data = client.get("/equipment").get_json()
    assert "equipment" in data
    assert isinstance(data["equipment"], list)
    assert len(data["equipment"]) > 0

def test_equipment_has_status_field(client):
    data = client.get("/equipment").get_json()
    for item in data["equipment"]:
        assert "status" in item


# ── CALORIES ─────────────────────────────────────────────────────────────────
def test_calories_with_weight_returns_200(client):
    assert client.get("/calories?weight=70").status_code == 200

def test_calories_returns_calculation(client):
    data = client.get("/calories?weight=70").get_json()
    assert "daily_calories_kcal" in data
    assert data["daily_calories_kcal"] > 0

def test_calories_without_weight_returns_400(client):
    assert client.get("/calories").status_code == 400

def test_calories_muscle_gain_higher_than_fat_loss(client):
    fat_loss = client.get("/calories?weight=70&program=Fat Loss").get_json()
    muscle_gain = client.get("/calories?weight=70&program=Muscle Gain").get_json()
    assert muscle_gain["daily_calories_kcal"] > fat_loss["daily_calories_kcal"]


# ── 404 HANDLING ──────────────────────────────────────────────────────────────
def test_unknown_route_returns_404(client):
    assert client.get("/nonexistent-route").status_code == 404

def test_another_unknown_route_returns_404(client):
    assert client.get("/admin/secret").status_code == 404
