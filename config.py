from os.path import dirname, realpath

TOKEN = '5063051229:AAGqfNAOll-gEQ56VIoBRuZA9vnZV5ETgA0'  # bot token from @BotFather

BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
PASSWORDS = {'758913011': 'OjS29XWqUnAWay81bmCv1GG3MOgyFvOkif8wozYe9mI='}
STATUS_CHANNEL = -740175445
SECTIONS = ['Diet', 'Costs', 'To-do', 'Settings']

GENERAL_CONFIG_PATH = BOT_PATH + '/general_config.ini'
PRODUCTS_DATABASE_PATH = BOT_PATH + '/data/Databases/cpfc.csv'
GUIDES_PATH = BOT_PATH + '/data/Guides'

USER_CONFIG_PATH = BOT_PATH + '/data/Users/{}/user_config.ini'
COSTS_CONFIG_PATH = BOT_PATH + '/data/Users/{}/costs/costs_config.ini'
DIET_CONFIG_PATH = BOT_PATH + '/data/Users/{}/diet/diet_config.ini'
TODO_CONFIG_PATH = BOT_PATH + '/data/Users/{}/todo/todo_config.ini'

COSTS_HISTORY_PATH = BOT_PATH + '/data/Users/{}/costs/costs_history.csv'
