from os.path import dirname, realpath

TOKEN = 'there should be a token here'  # bot token from @BotFather

BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
PASSWORDS = {}
STATUS_CHANNEL = False # ID of status channel. Enter anything (False for example) if status channel doesn't exist

COSTS_HISTORY_PATH = BOT_PATH + '/data/{}/costs/costs-history.csv'
GENERAL_CONFIG_PATH = BOT_PATH + '/general_config.ini'
USER_CONFIG_PATH = BOT_PATH + '/data/{}/user_config.ini'
