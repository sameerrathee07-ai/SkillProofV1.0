from fastapi.testclient import TestClient
from main import app
from database import Base, engine, get_db
from sqlalchemy.orm import Session
import models

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_signup():
    r = client.post("/api/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    return data["access_token"]

def test_login():
    r = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    return data["access_token"]

def test_me(token):
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["token_balance"] == 20

def test_start_session(token):
    r = client.post("/api/session/start", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    data = r.json()
    assert "session_id" in data
    assert data["current_step"] == 1
    assert "message" in data
    return data["session_id"]

def test_chat_flow(token, session_id):
    # Step 1: Idea
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["current_step"] == 2
    assert data["pitch_complete"] == False
    assert data["remaining_tokens"] == 18

    # Step 2: Customer
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["current_step"] == 3
    assert data["remaining_tokens"] == 16

    # Step 3: Business Model
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "We charge 49 rupees monthly for students and 99 rupees yearly for teams who pay per subscription."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["current_step"] == 4
    assert data["remaining_tokens"] == 14

    # Step 4: Competition
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "ChatGPT, Claude and Grammarly give generic advice, but PitchPal uniquely validates structure step by step."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["current_step"] == 5
    assert data["remaining_tokens"] == 12

    # Step 5: Team
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "I have five years of experience building fintech products and my unfair advantage is direct access to bank data."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["pitch_complete"] == True
    assert data["remaining_tokens"] == 10
    return session_id

def test_score(token, session_id):
    r = client.post("/api/session/score", headers={"Authorization": f"Bearer {token}"}, json={"session_id": session_id})
    assert r.status_code == 200
    data = r.json()
    assert "problem_clarity" in data
    assert "market_specificity" in data
    assert "revenue_viability" in data
    assert "competitive_awareness" in data
    assert "team_credibility" in data
    assert "investor_readiness" in data
    assert "feedback" in data
    for k in ["problem_clarity", "market_specificity", "revenue_viability", "competitive_awareness", "team_credibility", "investor_readiness"]:
        assert 1 <= data[k] <= 10
    return data

def test_pdf(token, session_id):
    r = client.post("/api/pdf/generate", headers={"Authorization": f"Bearer {token}"}, json={"session_id": session_id})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 1000

def test_tokens_purchase(token):
    r = client.post("/api/tokens/purchase", headers={"Authorization": f"Bearer {token}"}, json={"package": "basic"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] == True
    assert data["tokens_added"] == 20
    assert data["new_balance"] == 30

def test_history(token):
    r = client.get("/api/session/history", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    return data[0]["id"]

def test_session_detail(token, session_id):
    r = client.get(f"/api/session/{session_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == session_id
    assert "messages" in data
    assert len(data["messages"]) >= 11  # opening + 5 user + 5 assistant

def test_validation_pushback(token):
    session_id = test_start_session(token)
    # Weak answer - should push back
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "Short."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["current_step"] == 1  # Stays on step 1
    assert "too vague" in data["reply"].lower()

def test_insufficient_tokens():
    # Create new user
    r = client.post("/api/auth/signup", json={"email": "poor@example.com", "password": "password123"})
    token = r.json()["access_token"]
    
    # Use all 20 tokens (10 messages)
    session_id = test_start_session(token)
    for i in range(10):
        r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
            "session_id": session_id,
            "content": "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them."
        })
    
    # 11th message should fail
    r = client.post("/api/session/chat", headers={"Authorization": f"Bearer {token}"}, json={
        "session_id": session_id,
        "content": "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback."
    })
    assert r.status_code == 402

def run_all():
    print("Testing signup...")
    token = test_signup()
    print("OK signup")
    
    print("Testing login...")
    token = test_login()
    print("OK login")
    
    print("Testing /me...")
    test_me(token)
    print("OK /me")
    
    print("Testing start session...")
    session_id = test_start_session(token)
    print("OK start session")
    
    print("Testing chat flow (5 steps)...")
    test_chat_flow(token, session_id)
    print("OK chat flow")
    
    print("Testing score...")
    scores = test_score(token, session_id)
    print("OK score", scores)
    
    print("Testing PDF generation...")
    test_pdf(token, session_id)
    print("OK PDF")
    
    print("Testing token purchase...")
    test_tokens_purchase(token)
    print("OK token purchase")
    
    print("Testing history...")
    session_id = test_history(token)
    print("OK history")
    
    print("Testing session detail...")
    test_session_detail(token, session_id)
    print("OK session detail")
    
    print("Testing validation pushback...")
    test_validation_pushback(token)
    print("OK validation pushback")
    
    print("Testing insufficient tokens...")
    test_insufficient_tokens()
    print("OK insufficient tokens")
    
    print("\n=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    run_all()