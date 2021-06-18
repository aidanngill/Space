import json
import pytest
from io import BytesIO

def test_get_invite(client, app):
    # Valid invite code
    response = client.get("/invite/hjfv4Kmw1uQE77VmIVSDm178EIbTVsqh")
    assert response.status_code == 200

    # Deleted invite code
    response = client.get("/invite/vOLeHOwoKO3mvOAbntO34odCvu57pgl7")
    assert response.status_code == 404

    # Random invite code
    response = client.get("/invite/invalidInviteCodeAbcdef123456789")
    assert response.status_code == 404

def test_create_invite(client):
    for _ in range(4):
        assert client.put("/user/invites", data={
            "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q"
        }).status_code == 200

    assert client.put("/user/invites", data={
        "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q"
    }).status_code == 403

@pytest.mark.parametrize(
    "code,status",
    [
        ("hjfv4Kmw1uQE77VmIVSDm178EIbTVsqh", 204), # Valid invite
        ("QPPN41ePHKdC93C493tStVB5tFilsJ7B", 403), # Valid invite, not owned by user
        ("vOLeHOwoKO3mvOAbntO34odCvu57pgl7", 404)  # Deleted/inactive invite
    ]
)
def test_delete_invite(client, code, status):
    assert client.delete(f"/invite/{code}", json={
        "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q"
    }).status_code == status

def test_invite_page(client):
    response = client.get("/user/invites/1", query_string={
        "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q"
    })

    assert response.status_code == 200
    assert len(json.loads(response.data.decode())["invites"]) == 2

def test_file_upload(client):
    response = client.put("/file", data={
        "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q",
        "file": (BytesIO(b"example"), "example.txt")
    }, content_type="multipart/form-data")

    assert response.status_code == 200
    assert json.loads(response.data.decode())["user"] == 1

@pytest.mark.parametrize(
    "file,status",
    [
        ("owned-self.txt", 204),
        ("owned-other.txt", 403),
        ("non-existent-file.txt", 400),
        ("anonymous.txt", 403)
    ]
)
def test_file_delete(client, app, file, status):
    response = client.delete("/file", json={
        "apikey": "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q",
        "file": file
    })

    assert response.status_code == status
