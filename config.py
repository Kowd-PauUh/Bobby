"""
Created by Ivan Danylenko
Date 22.12.2021
"""

from os.path import dirname, realpath

TOKEN = '5063051229:AAGqfNAOll-gEQ56VIoBRuZA9vnZV5ETgA0'  # bot token from @BotFather
BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
COSTS_HISTORY_PATH = BOT_PATH + '/data/costs/costs-history.csv'
USER_CONFIG_PATH = BOT_PATH + '/user_config.ini'
