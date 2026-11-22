import pytest

REGISTER_URL = "/api/v1/auth/register"


async def test_register_creates_a_user(client, user_payload):
    response = await client.post(REGISTER_URL, json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "User_RPG"
    assert body["email"] == "user@example.com"
    assert "id" in body


async def test_register_never_returns_password_data(client, user_payload):
    response = await client.post(REGISTER_URL, json=user_payload)

    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body
    assert user_payload["password"] not in response.text


async def test_register_normalizes_email_to_lowercase(client, user_payload):
    payload = {**user_payload, "email": "User@Example.COM"}

    response = await client.post(REGISTER_URL, json=payload)

    assert response.json()["email"] == "user@example.com"


async def test_register_rejects_duplicate_email(client, registered_user):
    duplicate = {**registered_user, "username": "someone_else"}

    response = await client.post(REGISTER_URL, json=duplicate)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


async def test_register_rejects_duplicate_username_in_any_case(
    client, registered_user
):
    # Relies on the citext column: "user_rpg" and "User_RPG" are the same username.
    duplicate = {
        **registered_user,
        "username": "user_rpg",
        "email": "other@example.com",
    }

    response = await client.post(REGISTER_URL, json=duplicate)

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already taken"


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"password": "short"}, id="password-too-short"),
        pytest.param({"password": "x" * 129}, id="password-too-long"),
        pytest.param({"username": "ab"}, id="username-too-short"),
        pytest.param({"username": "a" * 31}, id="username-too-long"),
        pytest.param({"username": "bad name!"}, id="username-invalid-characters"),
        pytest.param({"email": "not-an-email"}, id="invalid-email"),
        pytest.param({"is_admin": True}, id="unknown-field"),
    ],
)
async def test_register_rejects_invalid_input(client, user_payload, changes):
    response = await client.post(REGISTER_URL, json={**user_payload, **changes})

    assert response.status_code == 422


async def test_validation_errors_do_not_echo_the_input(client, user_payload):
    rejected_password = "p4ss"

    response = await client.post(
        REGISTER_URL, json={**user_payload, "password": rejected_password}
    )

    assert response.status_code == 422
    assert rejected_password not in response.text
    assert all("input" not in error for error in response.json()["detail"])