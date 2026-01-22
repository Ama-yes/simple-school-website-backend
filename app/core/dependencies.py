from app.db.database import localSession





def get_database():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


