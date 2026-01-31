from app.core.security import password_hashing
from app.models.models import Admin
import asyncio, time


async def test_concurrent_logins(client, db_session):
    admin_password = "Test123456"
    hashed = password_hashing(admin_password)
    
    new_admin = Admin(username="test-admin", email="admin@test.com", hashed_password=hashed, token_version=1)
    
    db_session.add(new_admin)
    await db_session.commit()
    
    payload = {"username": "test-admin", "password": admin_password}
    
    tasks = []
    for _ in range(5):
        tasks.append(client.post(url="/admin/login", json=payload))
    
    start = time.perf_counter()
    responses = await asyncio.gather(*tasks)
    end = time.perf_counter()
    
    print(end - start)
    
    for resp in responses:
        assert resp.status_code == 200