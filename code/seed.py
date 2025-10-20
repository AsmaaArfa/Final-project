import os
from .database import get_session
from . import crud, models


def ensure_role(db, role_name: str, description: str = None):
    r = db.query(models.Role).filter_by(name=role_name).first()
    if r:
        return r
    return crud.create_role(db, name=role_name, description=description or f"{role_name} role")


def seed_initial_data():
    db = get_session()
    try:
        # ensure 'user' and 'admin' roles exist
        user_role = ensure_role(db, 'user', 'Regular user')
        admin_role = ensure_role(db, 'admin', 'Administrator')

        # seed admin user if env vars provided and user doesn't exist
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_email = os.getenv('ADMIN_EMAIL', f"{admin_username or 'admin'}@example.com")
        if admin_username and admin_password:
            exists = db.query(models.User).filter_by(username=admin_username).first()
            if not exists:
                # hash password using auth helper
                from .auth import get_password_hash
                hashed = get_password_hash(admin_password)
                user = crud.create_user(db, username=admin_username, email=admin_email, full_name=admin_username, hashed_password=hashed)
                # attach admin role
                user.roles.append(admin_role)
                db.commit()
    finally:
        db.close()
