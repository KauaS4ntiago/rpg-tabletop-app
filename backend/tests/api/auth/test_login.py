LOGIN_URL = "/api/v1/auth/login"


async def test_login_returns_a_bearer_token(client, registered_user):
    response = await client.post(
        LOGIN_URL,
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert response.headers["cache-control"] == "no-store"


async def test_login_ignores_email_case(client, registered_user):
    response = await client.post(
        LOGIN_URL,
        json={"email": "USER@EXAMPLE.COM", "password": registered_user["password"]},
    )

    assert response.status_code == 200


async def test_login_failures_are_indistinguishable(client, registered_user):
    wrong_password = await client.post(
        LOGIN_URL,
        json={"email": registered_user["email"], "password": "wrong-password"},
    )
    unknown_email = await client.post(
        LOGIN_URL,
        json={"email": "nobody@example.com", "password": "wrong-password"},
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.headers["www-authenticate"] == "Bearer"