from app.db import Base, SessionLocal, engine
from app.repository import create_profile
from app.schemas import ProfileCreate

Base.metadata.create_all(bind=engine)

seed_profiles = [
    ProfileCreate(user_id="user-001", full_name="Asha Rao", email="asha@example.com", role="student"),
    ProfileCreate(user_id="user-002", full_name="Rohan Mehta", email="rohan@example.com", role="mentor"),
]

with SessionLocal() as db:
    for profile in seed_profiles:
        try:
            create_profile(db, profile)
        except Exception:
            db.rollback()

print("Seed data inserted")
