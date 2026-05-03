import os

from dotenv import dotenv_values, load_dotenv

from src.ntchat_bot import PROJECT_ROOT

config = dotenv_values(PROJECT_ROOT / ".env")

data_dir_env = config.get("DATA_DIR", "${HOME}/Data/ntchat_bot")
DATA_DIR = os.path.expandvars(data_dir_env)
DATA_DIR = os.path.expanduser(DATA_DIR)

LOG_DIR = os.path.join(DATA_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "wechat.db")

LOG_LEVEL = config.get("LOG_LEVEL", "DEBUG")

WECHAT_AUTO_REPLY_ENABLED = config.get("WECHAT_AUTO_REPLY_ENABLED", "true").lower() == "true"
WECHAT_GROUP_REPLY_ENABLED = config.get("WECHAT_GROUP_REPLY_ENABLED", "true").lower() == "true"
WECHAT_CONTACT_REPLY_ENABLED = config.get("WECHAT_CONTACT_REPLY_ENABLED", "true").lower() == "true"

MESSAGE_SAVE_ENABLED = config.get("MESSAGE_SAVE_ENABLED", "true").lower() == "true"
CONTACT_SYNC_ENABLED = config.get("CONTACT_SYNC_ENABLED", "true").lower() == "true"
CHATROOM_SYNC_ENABLED = config.get("CHATROOM_SYNC_ENABLED", "true").lower() == "true"

DEBUG_MODE = config.get("DEBUG_MODE", "false").lower() == "true"

TEST_GROUP_ID = config.get("TEST_GROUP_ID", "")