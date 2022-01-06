from os.path import dirname, realpath

TOKEN = 'there should be a token here'  # bot token from @BotFather
USERS_WITH_ACCESS = [1111111111] # IDs of users with access
STATUS_CHANNEL = 1111111111 # ID of status channel

BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
COSTS_HISTORY_PATH = BOT_PATH + '/data/costs/costs-history.csv'
USER_CONFIG_PATH = BOT_PATH + '/user_config.ini'
