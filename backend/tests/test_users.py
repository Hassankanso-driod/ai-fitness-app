
def test_get_user(client):
    # Create user
    reg_res = client.post(
        "/register",
        json={
            "first_name": "getuser",
            "password": "password123",
            "email": "get@example.com",
            "age": 20,
            "weight_kg": 70,
            "height_cm": 170,
            "sex": "male",
            "goal": "maintain"
        },
    )
    user_id = reg_res.json()["id"]

    # Get user
    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "getuser"
    assert data["bmi"] is not None  # Should be calculated
    assert data["bmr"] is not None  # Should be calculated

def test_get_user_not_found(client):
    response = client.get("/user/99999")
    assert response.status_code == 404

def test_update_user(client):
    # Create user
    reg_res = client.post(
        "/register",
        json={
            "first_name": "updateuser",
            "password": "password123",
            "email": "update@example.com",
            "age": 30,
            "weight_kg": 80,
            "height_cm": 180,
            "goal": "lose_weight",
            "sex": "male"
        },
    )
    user_id = reg_res.json()["id"]
    
    # Update goal and weight
    response = client.put(
        f"/user/{user_id}",
        json={
            "goal": "gain_muscle",
            "weight_kg": 85
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["goal"] == "gain_muscle"
    assert data["weight_kg"] == 85.0
    
    # Verify persistence
    get_res = client.get(f"/user/{user_id}")
    assert get_res.json()["goal"] == "gain_muscle"
    assert get_res.json()["weight_kg"] == 85.0

def test_update_user_not_found(client):
    response = client.put("/user/99999", json={"goal": "test"})
    assert response.status_code == 404
