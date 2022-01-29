from configparser import ConfigParser
import telebot
from os.path import exists
from threading import Lock
from datetime import datetime as dt

from config import TOKEN, USER_CONFIG_PATH, GENERAL_CONFIG_PATH, BOT_PATH, PASSWORDS, COSTS_HISTORY_PATH
import src.new_handlers as nh
import src.general_functions as gf
import src.auxiliary_functions as af
import src.cyclic_functions as cf

bot = nh.TeleBot(TOKEN)
bot.cyclic_actions = []

USER_CONFIG = ConfigParser()
SECTIONS = ['Diet', 'Costs', 'To-do', 'Settings']
STATUS_MESSAGE_ID = [False]  # ID of the message in which the bot actualize his status
PREVIOUS_STATUS = ['DD.MM.YYYY hh:mm(ss)']
lock = Lock()


@bot.message_handler(commands=['start'])
def start(message):
    lock.acquire()
    gf.access_check(bot, message)
    af.check_user_files(bot, message)

    if message.chat.type == 'private':
        # keyboard
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for section in SECTIONS:
            markup.add(telebot.types.KeyboardButton(section))

        bot.send_message(message.chat.id, 'Let\'s start!', reply_markup=markup)
    lock.release()


@bot.message_handler(content_types=['text'])
def loop(message):
    lock.acquire()
    gf.access_check(bot, message)
    gf.create_status_message(bot, message, STATUS_MESSAGE_ID)

    user_id = message.from_user.id

    if message.chat.type == 'private':
        af.check_user_files(bot, message)
        gf.password_check(bot, message)

        if message.text in SECTIONS:  # section selection

            bot.send_message(message.chat.id, 'You are in the category "' + message.text + '".')
            if message.text == 'Settings':
                gf.show_current_settings(bot, message)

            af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
            try:
                USER_CONFIG.read(USER_CONFIG_PATH.format(user_id))
                USER_CONFIG['General']['section'] = message.text
                with open(USER_CONFIG_PATH.format(user_id), 'w') as configfile:
                    USER_CONFIG.write(configfile)
            except Exception as e:
                af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
                raise e
            af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
            lock.release()
            return

        else:
            af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
            try:
                USER_CONFIG.read(USER_CONFIG_PATH.format(user_id))
                section = USER_CONFIG['General']['section']
            except Exception as e:
                af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
                raise e
            af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])

            if section == 'Costs':
                if message.text == 'Stats':
                    gf.show_costs_stats(bot, message, 'Stats', USER_CONFIG)
                    lock.release()
                    return

                gf.purchase_handler(bot, message)  # add purchase

            if section == 'Settings':
                if message.text == 'Reset':
                    gf.load_default_settings(bot, message)
                    lock.release()
                    return

                gf.update_settings(bot, message, USER_CONFIG)
    lock.release()


@bot.cyclic_actions_handler()
def cyclic_actions_manager(_):
    lock.acquire()
    gf.update_status_message(bot, STATUS_MESSAGE_ID, PREVIOUS_STATUS)
    general_config = ConfigParser()
    general_config.read(GENERAL_CONFIG_PATH)
    users_with_access = general_config['General']['USERS_WITH_ACCESS'].split(',')
    for user_id in users_with_access:
        if exists(BOT_PATH + '/data/' + user_id) and user_id in PASSWORDS:
            user_id = int(user_id)
            af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
            af.decrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
            try:
                cf.show_weekly_costs_stats(bot=bot, user_config=USER_CONFIG,
                                           config_path=USER_CONFIG_PATH, user_id=user_id)
                cf.show_monthly_costs_stats(bot=bot, user_config=USER_CONFIG,
                                            config_path=USER_CONFIG_PATH, user_id=user_id)
                cf.send_good_morning(bot=bot, user_config=USER_CONFIG,
                                     config_path=USER_CONFIG_PATH, user_id=user_id)
            except Exception as e:
                af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
                af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
                raise e
            af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
            af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
    lock.release()


# RUN
while True:
    try:
        try:
            lock.release()
        except RuntimeError:
            pass
        bot.polling(none_stop=True)
    except Exception as err:
        print(f"[{dt.now():%d.%m.%Y %H:%M(%S)}]  Restarting...  The reason is: " + str(err))
