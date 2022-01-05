"""
Created by Ivan Danylenko
Date 22.12.2021
"""

from os.path import dirname, realpath

TOKEN = 'there should be a token here'  # bot token from @BotFather
BOT_PATH = dirname(realpath(__file__)).replace('\\', '/')  # .../Bobby
COSTS_HISTORY_PATH = BOT_PATH + '/data/costs/costs-history.csv'
USER_CONFIG_PATH = BOT_PATH + '/user_config.ini'
