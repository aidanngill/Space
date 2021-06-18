import pytest

from space.models import User

def test_register_no_invite(client, app):
    with app.app_context():
        app.config["INVITE_ONLY"] = False

    response = client.post("/auth/register", data={
        "email": "register_no_invite@example.com",
        "username": "register_no_invite",
        "password": "password"
    })

    assert response.status_code == 200

    with app.app_context():
        assert User.query.filter_by(
            username="register_no_invite",
            active=True
        ).count() > 0

@pytest.mark.parametrize(
    "code,status",
    [
        ("", 400),
        ("3ag25TZnKO3IumvbMaG6fZObYNGMlEsJ", 400), # Used
        ("vOLeHOwoKO3mvOAbntO34odCvu57pgl7", 400), # Deleted
        ("hjfv4Kmw1uQE77VmIVSDm178EIbTVsqh", 200)  # Unused
    ]
)
def test_register_with_invite(client, app, code, status):
    with app.app_context():
        app.config["INVITE_ONLY"] = True

    response = client.post("/auth/register", data={
        "email": f"{code[:3]}-{status}@example.com",
        "username": f"{code[:3]}-{status}",
        "password": "password",
        "invite": code
    })

    assert response.status_code == status

@pytest.mark.parametrize(
    "email,username,password,status",
    [
        ("invalidemail", "", "", 400),
        ("validate_input@example.com", "", "", 400),
        ("validate_input@example.com", "validate_input", "", 400),
        ("validate_input@example.com", "validate_input", "password", 200)
    ]
)
def test_register_validate_input(client, app, email, username, password, status):
    with app.app_context():
        app.config["INVITE_ONLY"] = False

    response = client.post("/auth/register", data={
        "email": email,
        "username": username,
        "password": password
    })

    assert response.status_code == status

def test_register_taken(client, app):
    with app.app_context():
        app.config["INVITE_ONLY"] = False

    # Create initial user
    response = client.post("/auth/register", data={
        "email": "taken1@example.com",
        "username": "taken1",
        "password": "password"
    })

    assert response.status_code == 200

    # Try creating users with same username/email
    for idx in range(2):
        response = client.post("/auth/register", data={
            "email": f"taken{idx + 1!r}@example.com",
            "username": f"taken{2 - idx!r}",
            "password": "password"
        })

        assert response.status_code == 400

@pytest.mark.parametrize(
    "username,password,status",
    [
        ("user", "passw0rd", 403),
        ("us3r", "password", 404),
        ("user", "password", 200)
    ]
)
def test_login(client, username, password, status):
    response = client.post("/auth/login", data={
        "username": username,
        "password": password
    })

    assert response.status_code == status
