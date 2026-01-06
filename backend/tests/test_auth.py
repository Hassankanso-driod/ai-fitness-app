
def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "first_name": "testuser",
            "password": "password123",
            "email": "test@example.com",
            "age": 25,
            "weight_kg": 70,
            "height_cm": 175,
            "goal": "lose_weight",
            "sex": "male"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user(client):
    payload = {
        "first_name": "duplicate",
        "password": "password123",
        "email": "dup@example.com",
        "age": 25,
        "weight_kg": 70,
        "height_cm": 175,
        "goal": "lose_weight",
        "sex": "female"
    }
    # First registration
    client.post("/register", json=payload)
    # Second registration
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_login_success(client):
    # Register first
    client.post(
        "/register",
        json={
            "first_name": "loginuser",
            "password": "password123",
            "email": "login@example.com",
            "age": 30,
            "weight_kg": 80,
            "height_cm": 180,
            "goal": "gain_muscle",
            "sex": "male"
        },
    )
    
    # Login
    response = client.post(
        "/login",
        json={
            "username_or_email": "login@example.com",
            "password": "password123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["first_name"] == "loginuser"

def test_login_invalid_credentials(client):
    client.post(
        "/register",
        json={
            "first_name": "wrongpass",
            "password": "password123",
            "email": "wrong@example.com",
            "sex": "male"
        },
    )
    
    response = client.post(
        "/login",
        json={
            "username_or_email": "wrong@example.com",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_nonexistent_user(client):
    response = client.post(
        "/login",
        json={
            "username_or_email": "nobody@example.com",
            "password": "password123"
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
