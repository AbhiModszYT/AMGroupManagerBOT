import threading
from sqlalchemy import Column, String
from Am.Database import BASE, SESSION
class ForwardChats(BASE):
    __tablename__ = "forward_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

ForwardChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()



def is_forward(chat_id):
    try:
        chat = SESSION.query(ForwardChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def set_forward(chat_id):
    with INSERTION_LOCK:
        forwardchat = SESSION.query(ForwardChats).get(str(chat_id))
        if not forwardchat:
            forwardchat = ForwardChats(str(chat_id))
        SESSION.add(forwardchat)
        SESSION.commit()

def rem_forward(chat_id):
    with INSERTION_LOCK:
        forwardchat = SESSION.query(ForwardChats).get(str(chat_id))
        if forwardchat:
            SESSION.delete(forwardchat)
        SESSION.commit()


def get_all_forward_chats():
    try:
        return SESSION.query(ForwardChats.chat_id).all()
    finally:
        SESSION.close()