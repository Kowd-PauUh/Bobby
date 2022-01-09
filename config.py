from os.path import dirname, realpath

TOKEN = 'there should be a token here'  # bot token from @BotFather
BOT_ID = False  # needed to update the status message. Enter anything (False for example) if you don't know what ID has your bot
USERS_WITH_ACCESS = [] # IDs of users with access
STATUS_CHANNEL = False # ID of status channel. Enter anything (False for example) if status channel doesn't exist

BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
COSTS_HISTORY_PATH = BOT_PATH + '/data/costs/costs-history.csv'
USER_CONFIG_PATH = BOT_PATH + '/user_config.ini'
