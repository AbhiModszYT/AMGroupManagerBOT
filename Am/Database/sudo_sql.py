import threading

from Am.Database import BASE, SESSION
from sqlalchemy import Column, BigInteger, UnicodeText


class ElevatedUsers(BASE):
    __tablename__ = "elevated_users"

    user_id = Column(BigInteger, primary_key=True)
    user_type = Column(UnicodeText)


ElevatedUsers.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def add_elevated_user(user_id: int, user_type: str):
    with INSERTION_LOCK:
        user = ElevatedUsers(user_id=user_id, user_type=user_type)
        SESSION.add(user)
        SESSION.commit()


def remove_elevated_user(user_id: int):
    user = SESSION.query(ElevatedUsers).filter_by(user_id=user_id).first()
    SESSION.delete(user)
    SESSION.commit()

def get_elevated_users_by_type(user_type: str):
    users = get_elevated_users()
    return [user for user in users if user.user_type == user_type]


def get_elevated_users():
    return SESSION.query(ElevatedUsers).all()
