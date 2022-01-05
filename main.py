"""
Created by Ivan Danylenko
Date 21.12.2021

Functions:
    section_[SectionName] - functions that are performed after selecting a section
    default_[SectionName] - functions performed after sending any message to the selected section
    (except the section switching message)
    command_[SectionName]_[CommandName] - functions that are performed after sending a specific instruction

"""

import telebot
import configparser
from config import TOKEN, COSTS_HISTORY_PATH, USER_CONFIG_PATH

from src.costs import add_purchase, stats_from_costs_in_the_period

bot = telebot.TeleBot(TOKEN)
USER_CONFIG = configparser.ConfigParser()
SECTIONS = ['Diet', 'Costs', 'To-do', 'Settings']
SECTION = 'no-section'


@bot.message_handler(commands=['start'])
def start(message):
    # keyboard
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for section in SECTIONS:
        markup.add(telebot.types.KeyboardButton(section))

    bot.send_message(message.chat.id, 'Let\'s start!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def loop(message):
    if message.chat.type == 'private':
        global SECTION

        if message.text in SECTIONS:  # section selection
            SECTION = message.text
            bot.send_message(message.chat.id, 'You are in the category "' + message.text + '".')
            if SECTION == 'Settings':
                section_settings(message)
            return

        else:
            if SECTION == 'Costs':
                if message.text == 'Stats':
                    command_costs_stats(message)
                    return

                default_costs(message)  # add purchase

            if SECTION == 'Settings':
                default_settings(message)


def section_settings(message):
    bot.send_message(message.chat.id, 'Current settings:')
    settings = open(USER_CONFIG_PATH, 'r')
    bot.send_message(message.chat.id, settings.read())


def default_settings(message):
    text = message.text.split('\n')
    failures = []
    for line in text:
        if len(line.split(' ')) != 3:
            failures.append(line)
            continue

        USER_CONFIG.read(USER_CONFIG_PATH)
        section, variable, value = line.split(' ')
        if ' ' in section or ' ' in variable or ' ' in value or section not in USER_CONFIG.sections():
            failures.append(line)
            continue

        USER_CONFIG[section][variable] = value
        with open(USER_CONFIG_PATH, 'w') as configfile:
            USER_CONFIG.write(configfile)

    section_settings(message)
    failures = '\n'.join(failures)
    if failures:
        bot.send_message(message.chat.id, 'These commands cannot be processed:')
        bot.send_message(message.chat.id, failures)


def default_costs(message):
    failures = add_purchase(message.text)
    if failures:
        bot.send_message(message.chat.id, 'Oops... these costs could not be processed:')
        bot.send_message(message.chat.id, '\n'.join(failures))
    else:
        bot.send_message(message.chat.id, 'Like clockwork! Anything else?')


def command_costs_stats(message):
    USER_CONFIG.read(USER_CONFIG_PATH)

    period = USER_CONFIG.get('Stats', 'period')
    pieces = USER_CONFIG.getint('Stats', 'pieces')
    head = USER_CONFIG.getint('Stats', 'head')

    show_report = USER_CONFIG.getboolean('Stats', 'show_report')
    show_cpd = USER_CONFIG.getboolean('Stats', 'show_cpd')
    show_percentage = USER_CONFIG.getboolean('Stats', 'show_percentage')
    show_products = USER_CONFIG.getboolean('Stats', 'show_products')
    show_prices = USER_CONFIG.getboolean('Stats', 'show_sum')
    show_pie = USER_CONFIG.getboolean('Stats', 'show_pie')
    show_total = USER_CONFIG.getboolean('Stats', 'show_total')

    if show_report is False and show_pie is False:
        bot.send_message(message.chat.id, 'You don\'t get any statistics at the moment. Update the settings for the '
                                          'information you want to receive')
        return
    if (show_cpd, show_percentage, show_products, show_prices, show_total) == (False, False, False, False, False):
        show_report = False

    period, plot, stats, total, days = stats_from_costs_in_the_period(COSTS_HISTORY_PATH, period, pieces, head)

    lines = []
    for percent, product, price in stats:
        cpd = (str(round(price / days, 2)) + '/day') if show_cpd is True else ''
        percentage = str(percent) + '%' if show_percentage is True else ''
        product = product if show_products is True else ''
        price = str(price) if show_prices is True else ''
        line = [cpd, percentage, product, price]
        while '' in line:
            line.remove('')
        line = ' - '.join(line)
        lines.append(line)

    lines = '\n'.join(lines)
    bot.send_message(message.chat.id, 'Expenses for the period\n' + period)
    if show_pie is True:
        bot.send_photo(message.chat.id, plot)

    if show_report is True and show_total is True:
        bot.send_message(message.chat.id, lines + '\n\nTotal: ' + str(total) +
                         ' (' + str(round(total / days, 2)) + ' per day)')
    elif show_report is True and show_total is False:
        bot.send_message(message.chat.id, lines)


# RUN
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print('Something went wrong:\n\t' + str(err) + '\nRestarting...')
