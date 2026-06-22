from app.infrastructure.storage.db.session import engine

with engine.connect() as conn:
    print("DB connected successfully")