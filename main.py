from configparser import ConfigParser
from telebot.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from os.path import exists
from threading import Lock
from datetime import datetime as dt

from config import TOKEN, BOT_PATH, GENERAL_CONFIG_PATH, USER_CONFIG_PATH, PASSWORDS, DIET_CONFIG_PATH, SECTIONS
import src.new_handlers as nh
import src.general_functions as gf
import src.auxiliary_functions as af
import src.cyclic_functions as cf

bot = nh.TeleBot(TOKEN)
bot.cyclic_actions = []

USER_CONFIG = ConfigParser()
STATUS_MESSAGE_ID = [False]  # ID of the message in which the bot actualize his status
PREVIOUS_STATUS = ['DD.MM.YYYY hh:mm(ss)']
lock = Lock()


@bot.message_handler(commands=['start'])
def start(message):
    lock.acquire()
    user_id = message.from_user.id
    gf.access_check(bot, user_id)
    gf.check_user_files(bot, message)
    af.check_language(bot, user_id)

    if message.chat.type == 'private':
        # keyboard
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for section in SECTIONS:
            keyboard.add(KeyboardButton(af.get_word(user_id, section)))

        bot.send_message(user_id, af.get_phrase(user_id, 0), reply_markup=keyboard)
    lock.release()


@bot.message_handler(content_types=['text'])
def loop(message: Message):
    lock.acquire()
    user_id = message.from_user.id
    gf.access_check(bot, user_id)
    gf.create_status_message(bot, message, STATUS_MESSAGE_ID)

    if message.chat.type == 'private':
        gf.check_user_files(bot, message)
        af.check_language(bot, user_id)

        if af.check_for_keywords(bot, user_id, message.text) in SECTIONS:  # section selection

            gf.branching(bot, message, user_id)

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
                    gf.show_costs_stats(bot, message, 'Stats')
                    lock.release()
                    return

                gf.purchase_handler(bot, message)  # add purchase

            if section == 'Diet':
                config, _ = af.read_config(DIET_CONFIG_PATH, user_id)
                action = config['DontChangeIt']['action']
                if action == 'Modify allowed products':
                    if message.text == 'Reset':
                        gf.clear_products_list(bot, user_id, ['allowed'])
                    else:
                        af.new_products_handler(bot, message, 'allowed')
                elif action == 'Modify each-meal products':
                    if message.text == 'Reset':
                        gf.clear_products_list(bot, user_id, ['each-meal'])
                    else:
                        af.new_products_handler(bot, message, 'each-meal')
                else:
                    if message.text == 'Reset':
                        gf.clear_products_list(bot, user_id, ['allowed', 'each-meal'])

            if section == 'Settings':
                config, _ = af.read_config(USER_CONFIG_PATH, user_id)
                settings_section = config['DontChangeIt']['settings_section']

                if message.text == 'Reset':
                    gf.load_default_settings(bot, message, settings_section)
                    lock.release()
                    return

                gf.update_settings(bot, message, settings_section)
    lock.release()


@bot.callback_query_handler(func=lambda callback: True)
def keyboard_actions_manager(callback: CallbackQuery):
    lock.acquire()

    user_id = callback.from_user.id
    gf.access_check(bot, user_id)
    if str(user_id) not in PASSWORDS:
        bot.send_message(user_id, af.get_phrase(user_id, 1))
        lock.release()
        return

    try:
        config, _ = af.read_config(USER_CONFIG_PATH, user_id)
    except FileNotFoundError:
        bot.send_message(user_id, af.get_phrase(user_id, 2))
        lock.release()
        return

    gf.keyboard_replies_manager(bot, callback)
    lock.release()


@bot.cyclic_actions_handler()
def cyclic_actions_manager(_):
    lock.acquire()
    gf.update_status_message(bot, STATUS_MESSAGE_ID, PREVIOUS_STATUS)
    general_config = ConfigParser()
    general_config.read(GENERAL_CONFIG_PATH)
    users_with_access = general_config['General']['USERS_WITH_ACCESS'].split(',')

    for user_id in users_with_access:
        if exists(BOT_PATH + '/data/Users/' + user_id) and user_id in PASSWORDS:
            user_id = int(user_id)
            af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
            try:
                cf.show_weekly_costs_stats(bot=bot, config_path=USER_CONFIG_PATH, user_id=user_id)
                cf.show_monthly_costs_stats(bot=bot, config_path=USER_CONFIG_PATH, user_id=user_id)
                cf.send_good_morning(bot=bot, config_path=USER_CONFIG_PATH, user_id=user_id)
            except Exception as e:
                af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
                raise e
            af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
    lock.release()


# try:
#     bot.polling(none_stop=True)
# except:
#     lock.release()
#     bot.polling(none_stop=True)
# bot.polling(none_stop=True)

while True:
    try:
        try:
            lock.release()
        except RuntimeError:
            pass
        bot.polling(none_stop=True)
    except Exception as err:
        print(f"[{dt.now():%d.%m.%Y %H:%M(%S)}]  Restarting...  The reason is: " + str(err))
