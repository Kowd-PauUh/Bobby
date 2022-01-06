import configparser
import telebot

from config import TOKEN, USER_CONFIG_PATH
import src.new_handlers as nh
import src.general_functions as gf
import src.cyclic_functions as cf

bot = nh.TeleBot(TOKEN)
bot.cyclic_actions = []

USER_CONFIG = configparser.ConfigParser()
SECTIONS = ['Diet', 'Costs', 'To-do', 'Settings']
SECTION = 'no-section'
STATUS_MESSAGE_ID = [False]  # ID of the message in which the bot actualize his status
PREVIOUS_STATUS = ['DD.MM.YYYY hh:mm(ss)']


@bot.message_handler(commands=['start'])
def start(message):
    gf.access_check(bot, message)

    if message.chat.type == 'private':
        # keyboard
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for section in SECTIONS:
            markup.add(telebot.types.KeyboardButton(section))

        bot.send_message(message.chat.id, 'Let\'s start!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def loop(message):
    gf.access_check(bot, message)
    gf.create_status_message(bot, message, STATUS_MESSAGE_ID)

    if message.chat.type == 'private':
        global SECTION

        if message.text in SECTIONS:  # section selection
            SECTION = message.text
            bot.send_message(message.chat.id, 'You are in the category "' + message.text + '".')
            if SECTION == 'Settings':
                gf.show_current_settings(bot, message)
            return

        else:
            if SECTION == 'Costs':
                if message.text == 'Stats':
                    gf.show_costs_stats(bot, message.chat.id, 'Stats', USER_CONFIG)
                    return

                gf.purchase_handler(bot, message)  # add purchase

            if SECTION == 'Settings':
                gf.update_settings(bot, message, USER_CONFIG)


@bot.cyclic_actions_handler()
def cyclic_actions_manager(_):
    gf.update_status_message(bot, STATUS_MESSAGE_ID, PREVIOUS_STATUS)
    cf.show_weekly_costs_stats(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH)
    cf.show_monthly_costs_stats(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH)
    cf.send_good_morning(bot=bot, user_config=USER_CONFIG, config_path=USER_CONFIG_PATH)


# RUN
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print('Something went wrong:\n\t' + str(err) + '\nRestarting...')
