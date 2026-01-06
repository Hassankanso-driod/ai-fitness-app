from unittest.mock import patch

def test_get_supplements_empty(client):
    response = client.get("/supplements")
    assert response.status_code == 200
    assert response.json() == []

def test_create_supplement_no_image(client):
    response = client.post(
        "/supplements",
        data={
            "name": "Whey Protein",
            "description": "High quality protein",
            "price": 49.99
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Whey Protein"
    assert data["price"] == 49.99
    assert data["image_url"] is None

def test_create_supplement_with_image(client):
    # Patch the function in main.py where it's used
    with patch("main.save_uploaded_file", return_value="uploads/test.jpg"):
        response = client.post(
            "/supplements",
            data={
                "name": "Creatine",
                "description": "For muscle",
                "price": 29.99
            },
            files={"image": ("test.jpg", b"fakeimage", "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Creatine"
    assert data["image_url"] == "uploads/test.jpg"

def test_update_supplement(client):
    # Create first
    res = client.post(
        "/supplements",
        data={"name": "Old Name", "description": "Desc", "price": 10.0}
    )
    sup_id = res.json()["id"]

    # Update
    response = client.put(
        f"/supplements/{sup_id}",
        data={"name": "New Name", "price": 20.0}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["price"] == 20.0

def test_delete_supplement(client):
    # Create with image to test delete_uploaded_file interaction
    with patch("main.save_uploaded_file", return_value="uploads/todelete.jpg"):
        res = client.post(
            "/supplements",
            data={"name": "To Delete", "description": "...", "price": 5.0},
            files={"image": ("del.jpg", b"x", "image/jpeg")}
        )
    sup_id = res.json()["id"]

    # Delete
    with patch("main.delete_uploaded_file") as mock_delete:
        response = client.delete(f"/supplements/{sup_id}")
        assert response.status_code == 200
        assert mock_delete.called

    # Verify 404
    get_res = client.get(f"/supplements/{sup_id}")
    # main.py does not have GET /supplements/{id} but crud has get_supplement
    # The API only exposes GET /supplements (list).
    # But wait, DELETE relies on get_supplement so it should be gone.
    # We can check list.
    list_res = client.get("/supplements")
    assert len(list_res.json()) == 0
