async def test_health_returns_ok(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_db_reaches_the_test_database(client):
    response = await client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}