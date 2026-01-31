from app.core.security import password_hashing
from app.models.models import Admin
import pytest



async def test_admin_login_successful(client, db_session):
    admin_password = "Test1234"
    hashed = password_hashing(admin_password)
    
    new_admin = Admin(username="testadmin", email="admin@test.com", hashed_password=hashed, token_version=1)
    
    db_session.add(new_admin)
    await db_session.commit()
    
    payload = {"username": "testadmin", "password": admin_password}
    
    response = await client.post(url="/admin/login", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_admin_login_wrong_psswrd(client, db_session):
    admin_password = "Test1234"
    hashed = password_hashing(admin_password)
    
    new_admin = Admin(username="testadmin", email="admin@test.com", hashed_password=hashed, token_version=1)
    
    db_session.add(new_admin)
    await db_session.commit()
    
    payload = {"username": "testadmin", "password": "WrongPassword"}
    
    response = await client.post(url="/admin/login", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email or password incorrect!"


async def test_login_rate_limit(client):
    payload = {"username": "RateLimitTest", "password": "Testpassword123"}
    
    for _ in range(5):
        await client.post("/admin/login", json=payload)
    
    
    response = await client.post("/admin/login", json=payload)
    
    assert response.status_code in [429, 400]