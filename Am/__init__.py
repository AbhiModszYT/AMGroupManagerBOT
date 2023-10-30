import logging
import os
import sys
import time
import telegram.ext as tg
from telethon.sessions import MemorySession
from telethon import TelegramClient
from redis import StrictRedis
from pyrogram import Client, errors

StartTime = time.time()

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You must have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    TOKEN = os.environ.get("TOKEN", "")#bot token

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", ""))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")
    try:
        INSPECTOR = {int(x) for x in os.environ.get("INSPECTOR", "6204761408").split()}
        DEV_USERS = {int(x) for x in os.environ.get("DEV_USERS", "6204761408").split()}
    except ValueError:
        raise Exception(
            "Your inspector(sudo) or dev users list does not contain valid integers.")

    try:
        REQUESTER = {int(x) for x in os.environ.get("REQUESTER", "5360305806").split()}
    except ValueError:
        raise Exception("Your requester list does not contain valid integers.")
    try:
        API_ID = int(os.environ.get("API_ID", "12227067"))
    except ValueError:
        raise Exception("Your API_ID env variable is not a valid integer.")

    try:
        API_HASH = os.environ.get("API_HASH", "b463bedd791aa733ae2297e6520302fe")
    except ValueError:
        raise Exception("Please Add Hash Api key to start the bot")

    DB_URI = os.environ.get("DATABASE_URL","") #Sql db url
    WORKERS = int(os.environ.get("WORKERS", 8))
    ALLOW_EXCL = os.environ.get('ALLOW_EXCL', False)
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    CERT_PATH = os.environ.get("CERT_PATH")
    URL = os.environ.get("URL", "")  # Does not contain token
    PORT = int(os.environ.get("PORT", 5000))
    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD","").split()
    UPDATES = os.environ.get("UPDATES","AMBOTYT")
    BOT_USERNAME = os.environ.get("BOT_USERNAME","AM_YTBOTT")
    BOT_NAME = os.environ.get("BOT_NAME","Sophia")
    CHAT_GROUP = os.environ.get("CHAT_GROUP","AM_YTSUPPORT")
    GBANS = os.environ.get("GBANS","Logs_Gban")
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT","AM_YTSUPPORT")
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", True))
    INFOPIC = bool(os.environ.get("INFOPIC", False))
    REDIS_URL = os.environ.get("REDIS_URL","redis://default:mvwQl6zkrKuhD584XKB8kCOEB2Os8vlJ@redis-14834.c244.us-east-1-2.ec2.cloud.redislabs.com:14834")

else:
    from Am.config import Development as Config

    TOKEN = Config.TOKEN

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("ʏᴏᴜʀ OWNER_ID ᴠᴀʀɪᴀʙʟᴇ ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ.")

    JOIN_LOGGER = Config.JOIN_LOGGER
    OWNER_USERNAME = Config.OWNER_USERNAME
    ALLOW_CHATS = Config.ALLOW_CHATS
    try:
        INSPECTOR = {int(x) for x in Config.INSPECTOR or []}
        DEV_USERS = {int(x) for x in Config.DEV_USERS or []}
    except ValueError:
        raise Exception(
            "ʏᴏᴜʀ sᴜᴅᴏ ᴏʀ ᴅᴇᴠ ᴜsᴇʀs ʟɪsᴛ ᴅᴏᴇs ɴᴏᴛ ᴄᴏɴᴛᴀɪɴ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀs.")

    try:
        REQUESTER = {int(x) for x in Config.REQUESTER or []}
    except ValueError:
        raise Exception(
            "ʏᴏᴜʀ sᴜᴘᴘᴏʀᴛ ᴜsᴇʀs ʟɪsᴛ ᴅᴏᴇs ɴᴏᴛ ᴄᴏɴᴛᴀɪɴ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀs.")

    INFOPIC = Config.INFOPIC
    EVENT_LOGS = Config.EVENT_LOGS
    WEBHOOK = Config.WEBHOOK
    PORT = Config.PORT
    CERT_PATH = Config.CERT_PATH
    API_ID = Config.API_ID
    GBANS = Config.GBANS
    CHAT_GROUP = Config.CHAT_GROUP
    API_HASH = Config.API_HASH
    DB_URI = Config.DATABASE_URL
    STRICT_GBAN = Config.STRICT_GBAN
    BOT_USERNAME = Config.BOT_USERNAME
    BOT_NAME = Config.BOT_NAME
    WORKERS = Config.WORKERS
    DEL_CMDS = Config.DEL_CMDS
    LOAD = Config.LOAD
    UPDATES = Config.UPDATES
    NO_LOAD = Config.NO_LOAD
    # CASH_API_KEY = Config.CASH_API_KEY
    REDIS_URL = Config.REDIS_URL
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    # YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY
    PHOTO = Config.PHOTO
    ALLOW_EXCL = Config.ALLOW_EXCL

INSPECTOR.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
pbot = Client("AmPyro", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
telethn = TelegramClient("Amuncle", API_ID, API_HASH)
dispatcher = updater.dispatcher

REDIS = StrictRedis.from_url(REDIS_URL, decode_responses=True)
try:
    REDIS.ping()
    LOGGER.info("Your redis server is now alive!")
except BaseException:
    raise Exception("Your redis server is not alive, please check again.")
finally:
    REDIS.ping()
    LOGGER.info("Your redis server is now alive!")
