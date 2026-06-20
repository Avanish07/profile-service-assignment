from sqlalchemy.orm import Session

from app.models import Profile
from app.schemas import ProfileCreate, ProfileUpdate


def list_profiles(db: Session) -> list[Profile]:
    return db.query(Profile).order_by(Profile.id.asc()).all()


def get_profile(db: Session, user_id: str) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(db: Session, payload: ProfileCreate) -> Profile:
    profile = Profile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, user_id: str, payload: ProfileUpdate) -> Profile | None:
    profile = get_profile(db, user_id)
    if profile is None:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, user_id: str) -> bool:
    profile = get_profile(db, user_id)
    if profile is None:
        return False

    db.delete(profile)
    db.commit()
    return True
