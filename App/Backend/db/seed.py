from models.user import UserDB
from db.session import SessionLocal

TEMP_USER_EMAIL = "temp@dashboard.local"

# Set during startup by seed_temp_user(), used by analysis_service
temp_user_id: int = None


def seed_temp_user():
    global temp_user_id

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.user_email == TEMP_USER_EMAIL).first()

        if not user:
            user = UserDB(
                user_name="Temp User",
                user_email=TEMP_USER_EMAIL,
                password_hash="not-set",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Temp user created with ID: {user.user_id}")
        else:
            print(f"Temp user already exists with ID: {user.user_id}")

        temp_user_id = user.user_id

    finally:
        db.close()
