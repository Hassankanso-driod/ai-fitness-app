import pytest

@pytest.fixture
def test_user(client):
    response = client.post(
        "/register",
        json={
            "first_name": "featureuser",
            "password": "password",
            "email": "feature@test.com",
            "age": 25,
            "weight_kg": 75,
            "height_cm": 180,
            "sex": "male",
            "goal": "general_fitness"
        }
    )
    if response.status_code != 200:
        print(f"DEBUG: Register failed. Status: {response.status_code}, Body: {response.text}")
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def test_supplement(client):
    response = client.post(
        "/supplements",
        data={"name": "Feature Sup", "description": "Desc", "price": 20.0}
    )
    return response.json()

def test_favorites_flow(client, test_user, test_supplement):
    user_id = test_user["id"]
    sup_id = test_supplement["id"]

    # Add Favorite
    res = client.post(
        "/favorites", 
        json={"user_id": user_id, "supplement_id": sup_id}
    )
    assert res.status_code == 200
    fav_id = res.json()["id"]

    # Check Favorite
    check = client.get(f"/favorites/check/{user_id}/{sup_id}")
    assert check.json()["is_favorite"] is True

    # Get User Favorites
    user_favs = client.get(f"/favorites/user/{user_id}")
    assert len(user_favs.json()) == 1

    # Remove Favorite
    del_res = client.delete(f"/favorites/{fav_id}")
    assert del_res.status_code == 200

    # Verify Removal
    check = client.get(f"/favorites/check/{user_id}/{sup_id}")
    assert check.json()["is_favorite"] is False

def test_reminders_crud(client, test_user):
    user_id = test_user["id"]
    
    # Create
    res = client.post(
        "/reminders",
        json={
            "user_id": user_id,
            "type": "water",
            "time": "10:00"
        }
    )
    assert res.status_code == 200
    rem_id = res.json()["id"]

    # Get
    get_res = client.get(f"/reminders/user/{user_id}")
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["type"] == "water"

    # Delete
    del_res = client.delete(f"/reminders/{rem_id}")
    assert del_res.status_code == 200

    # Verify
    get_res = client.get(f"/reminders/user/{user_id}")
    assert len(get_res.json()) == 0

def test_water_intake(client, test_user):
    user_id = test_user["id"]

    # Add
    res = client.post(
        "/water",
        json={"user_id": user_id, "amount_ml": 250}
    )
    assert res.status_code == 200
    
    # Get
    get_res = client.get(f"/water/user/{user_id}")
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["amount_ml"] == 250

def test_progress_entries(client, test_user):
    user_id = test_user["id"]

    # Add
    res = client.post(
        "/progress",
        json={
            "user_id": user_id,
            "weight_kg": 74.5,
            "date": "2024-01-01"
        }
    )
    assert res.status_code == 200

    # Get
    get_res = client.get(f"/progress/user/{user_id}")
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["weight_kg"] == 74.5

def test_workout_logs(client, test_user):
    user_id = test_user["id"]
    
    # Add
    res = client.post(
        "/workout-logs",
        json={
            "user_id": user_id,
            "exercise_name": "Bench Press",
            "category": "Strength",
            "sets": 3,
            "reps": 10,
            "weight_kg": 60,
            "date": "2024-01-01"
        }
    )
    assert res.status_code == 200

    # Get
    get_res = client.get(f"/workout-logs/user/{user_id}")
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["exercise_name"] == "Bench Press"

def test_notifications(client, test_user):
    user_id = test_user["id"]

    # Create
    res = client.post(
        "/notifications",
        json={"user_id": user_id, "message": "Hello"}
    )
    assert res.status_code == 200
    notif_id = res.json()["id"]
    assert res.json()["status"] == "pending"

    # Get
    get_res = client.get(f"/notifications/user/{user_id}")
    assert len(get_res.json()) == 1

    # Update (Mark as read / seen)
    up_res = client.put(
        f"/notifications/{notif_id}",
        json={"status": "seen"}
    )
    assert up_res.status_code == 200
    
    # Verify update
    get_res = client.get(f"/notifications/user/{user_id}")
    assert get_res.json()[0]["status"] == "seen"
