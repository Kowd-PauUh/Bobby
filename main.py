import configparser
import telebot
from os.path import exists

from config import TOKEN, USER_CONFIG_PATH, GENERAL_CONFIG_PATH, BOT_PATH
import src.new_handlers as nh
import src.general_functions as gf
import src.auxiliary_functions as af
import src.cyclic_functions as cf

bot = nh.TeleBot(TOKEN)
bot.cyclic_actions = []

USER_CONFIG = configparser.ConfigParser()
SECTIONS = ['Diet', 'Costs', 'To-do', 'Settings']
STATUS_MESSAGE_ID = [False]  # ID of the message in which the bot actualize his status
PREVIOUS_STATUS = ['DD.MM.YYYY hh:mm(ss)']


@bot.message_handler(commands=['start'])
def start(message):
    gf.access_check(bot, message)
    af.check_user_files(message.from_user.id)

    if message.chat.type == 'private':
        # keyboard
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for section in SECTIONS:
            markup.add(telebot.types.KeyboardButton(section))

        bot.send_message(message.chat.id, 'Let\'s start!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def loop(message):
    gf.access_check(bot, message)
    af.check_user_files(message.from_user.id)
    gf.create_status_message(bot, message, STATUS_MESSAGE_ID)

    if message.chat.type == 'private':

        if message.text in SECTIONS:  # section selection

            bot.send_message(message.chat.id, 'You are in the category "' + message.text + '".')
            if message.text == 'Settings':
                gf.show_current_settings(bot, message)

            USER_CONFIG.read(USER_CONFIG_PATH.format(message.from_user.id))
            USER_CONFIG['General']['section'] = message.text
            with open(USER_CONFIG_PATH.format(message.from_user.id), 'w') as configfile:
                USER_CONFIG.write(configfile)
            return

        else:
            USER_CONFIG.read(USER_CONFIG_PATH.format(message.from_user.id))
            section = USER_CONFIG['General']['section']

            if section == 'Costs':
                if message.text == 'Stats':
                    gf.show_costs_stats(bot, message, 'Stats', USER_CONFIG)
                    return

                gf.purchase_handler(bot, message)  # add purchase

            if section == 'Settings':
                if message.text == 'Reset':
                    gf.load_default_settings(bot, message)
                    return

                gf.update_settings(bot, message, USER_CONFIG)


@bot.cyclic_actions_handler()
def cyclic_actions_manager(_):
    gf.update_status_message(bot, STATUS_MESSAGE_ID, PREVIOUS_STATUS)
    USER_CONFIG.read(GENERAL_CONFIG_PATH)
    users_with_access = USER_CONFIG['General']['USERS_WITH_ACCESS'].split(',')
    for user_id in users_with_access:
        if exists(BOT_PATH + '/data/' + user_id):
            user_id = int(user_id)
            cf.show_weekly_costs_stats(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH, user_id=user_id)
            cf.show_monthly_costs_stats(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH, user_id=user_id)
            cf.send_good_morning(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH, user_id=user_id)


# RUN
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print('Something went wrong:\n\t' + str(err) + '\nRestarting...')
