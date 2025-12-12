import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_session
from models import AppUser


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_credentials(username: str, password: str):
    with get_session() as session:
        stmt = select(AppUser).where(AppUser.username == username)
        user: AppUser | None = session.scalar(stmt)

    if user is None:
        return None

    if hash_password(password) != user.password_hash:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }
