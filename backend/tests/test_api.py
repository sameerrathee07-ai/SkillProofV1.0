import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models import User, TokenBalance
from app.auth import hash_password
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

client = TestClient(app)

TEST_PASSWORD_HASH = "$5$rounds=535000$Nah96kmdrPJ1zQGL$cRE5Yn4rOGLYkD1qnBKayUSWWHME27z1cfqk93sEzR2"  # "password123" with sha256_crypt

def get_test_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    user = User(email="test@example.com", password_hash=TEST_PASSWORD_HASH, name="Test User", role="solver")
    db.add(user)
    db.commit()
    db.refresh(user)
    balance = TokenBalance(user_id=user.id, balance=20)
    db.add(balance)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_signup():
    resp = client.post("/auth/signup", json={"email": "new@example.com", "password": "password123", "name": "New User", "role": "solver"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.cookies.get("access_token")

def test_login():
    resp = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_me():
    client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    resp = client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

def test_create_problem():
    client.post("/auth/signup", json={"email": "poster@example.com", "password": "password123", "name": "Poster", "role": "poster"})
    
    resp = client.post("/problems", json={
        "description": "We need an automated system to schedule hotel housekeeping shifts and alert managers when rooms are delayed. This will save hours of manual work.",
        "category": "Hospitality",
        "budget_range": "Rs 5000 per month",
        "timeline": "2 weeks"
    })
    assert resp.status_code == 200
    assert resp.json()["id"] == 1

def test_create_problem_validation_fails():
    client.post("/auth/signup", json={"email": "poster2@example.com", "password": "password123", "name": "Poster2", "role": "poster"})
    
    resp = client.post("/problems", json={
        "description": "Short desc.",
        "category": "Hospitality",
        "budget_range": "free",
        "timeline": "soon"
    })
    assert resp.status_code == 400
    assert "errors" in resp.json()

def test_list_problems():
    client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    resp = client.get("/problems")
    assert resp.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])