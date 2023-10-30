import threading
from sqlalchemy import Column, String
from Am.Database import BASE, SESSION
class AmChats(BASE):
    __tablename__ = "Am_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

AmChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_Am(chat_id):
    try:
        chat = SESSION.query(AmChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def set_Am(chat_id):
    with INSERTION_LOCK:
        Amchat = SESSION.query(AmChats).get(str(chat_id))
        if not Amchat:
            Amchat = AmChats(str(chat_id))
        SESSION.add(Amchat)
        SESSION.commit()

def rem_Am(chat_id):
    with INSERTION_LOCK:
        Amchat = SESSION.query(AmChats).get(str(chat_id))
        if Amchat:
            SESSION.delete(Amchat)
        SESSION.commit()


def get_all_Am_chats():
    try:
        return SESSION.query(AmChats.chat_id).all()
    finally:
        SESSION.close()