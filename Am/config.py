
import json
import os


def get_user_list(config, key):
    with open("{}/Am/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]

class Config(object):
    LOGGER = True

    API_ID = "12227067"
    API_HASH = "b463bedd791aa733ae2297e6520302fe"
    TOKEN = ""
    OWNER_ID = ""
    OWNER_USERNAME = ""
    UPDATES = ""
    SUPPORT_CHAT = "AM_YTSUPPORT"
    JOIN_LOGGER = "-1001841879487"
    EVENT_LOGS = "-1001841879487"
    BOT_USERNAME = ""
    BOT_NAME = ""
    GBANS = "AMBOTYT" 
    CHAT_GROUP = ""
    # 
    # DATABASE_URL = "postgres://ixweewbx:9OoB_feF6d6wK1W4YycgwHzRHQXezsNA@arjuna.db.elephantsql.com/ixweewbx"  # sql
    DATABASE_URL = ""  # sql
    LOAD = []
    NO_LOAD = []
    WEBHOOK = False
    REDIS_URL = "redis://default:725m47dhlmisA0QecURSMkcHNGXkM1uP@redis-15808.c275.us-east-1-4.ec2.cloud.redislabs.com:15808"

    INSPECTOR = get_user_list("elevated_users.json", "ins")
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    REQUESTER = get_user_list("elevated_users.json", "req")

    CERT_PATH = None
    STRICT_GBAN = True
    PORT = "8080"
    DEL_CMDS = True
    STRICT_GBAN = True
    WORKERS = 20
    ALLOW_EXCL = True
    ALLOW_CHATS = True
    PHOTO = "https://graph.org/file/2d3f35226a0d59cbb9980.jpg" # Miss Poppy Music Pic
    INFOPIC = True


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
