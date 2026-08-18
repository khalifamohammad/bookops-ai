from datetime import date, timedelta


def auth_headers(client):
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "TestPassword123!"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_booking_flow(client):
    services = client.get("/api/services").json()
    assert services
    service_id = services[0]["id"]
    day = date.today() + timedelta(days=1)
    availability = client.get("/api/availability", params={"service_id": service_id, "date": day.isoformat()})
    assert availability.status_code == 200
    slot = availability.json()["slots"][0]

    created = client.post("/api/bookings/public", json={
        "customer_name": "Test Customer",
        "customer_phone": "+972500000000",
        "service_id": service_id,
        "booking_date": day.isoformat(),
        "start_time": slot,
        "customer_notes": "Urgent before an event",
    })
    assert created.status_code == 201, created.text
    booking_id = created.json()["id"]

    headers = auth_headers(client)
    analyzed = client.post(f"/api/ai/analyze-booking/{booking_id}", headers=headers)
    assert analyzed.status_code == 200
    assert analyzed.json()["priority"] == "high"

    confirmed = client.patch(
        f"/api/bookings/{booking_id}/status",
        headers=headers,
        json={"status": "CONFIRMED"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMED"
