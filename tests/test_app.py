from src.app import activities

ACTIVITY = "Chess Club"
NEW_EMAIL = "newstudent@mergington.edu"


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert ACTIVITY in data
    assert set(data.keys()) == set(activities.keys())
    for details in data.values():
        assert expected_keys <= set(details.keys())


def test_signup_adds_participant(client):
    # Arrange
    assert NEW_EMAIL not in activities[ACTIVITY]["participants"]

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    assert NEW_EMAIL in activities[ACTIVITY]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    unknown = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{unknown}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    # Arrange
    existing = activities[ACTIVITY]["participants"][0]
    count_before = len(activities[ACTIVITY]["participants"])

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": existing})

    # Assert
    assert response.status_code == 400
    assert len(activities[ACTIVITY]["participants"]) == count_before


def test_unregister_removes_participant(client):
    # Arrange
    existing = activities[ACTIVITY]["participants"][0]

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/signup", params={"email": existing})

    # Assert
    assert response.status_code == 200
    assert existing not in activities[ACTIVITY]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    unknown = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{unknown}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404


def test_unregister_not_signed_up_returns_400(client):
    # Arrange
    assert NEW_EMAIL not in activities[ACTIVITY]["participants"]

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 400


def test_signup_then_unregister_restores_participants(client):
    # Arrange
    before = list(activities[ACTIVITY]["participants"])

    # Act
    signup = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})
    unregister = client.delete(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert signup.status_code == 200
    assert unregister.status_code == 200
    assert activities[ACTIVITY]["participants"] == before
