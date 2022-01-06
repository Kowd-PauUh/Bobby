from datetime import datetime
from telebot import TeleBot
from config import USER_CONFIG_PATH, USERS_WITH_ACCESS, STATUS_CHANNEL
import src.auxiliary_functions as af


def access_check(bot: TeleBot, message):
    user_id = message.from_user.id
    if user_id not in USERS_WITH_ACCESS:
        bot.send_message(message.chat.id, 'You do not have access to the bot.')
        raise ValueError('Attempted access by a user who does not have access. User ID: ' + str(user_id))


def create_status_message(bot: TeleBot, message, status_message_id: list):
    if message.chat.id != STATUS_CHANNEL:
        return

    if message.text == '/reset':
        bot.send_message(STATUS_CHANNEL, 'Reply with a text to any of my messages to turn it into a status message.')
        status_message_id[0] = True

    if status_message_id[0] is False:
        bot.send_message(STATUS_CHANNEL, 'Reply with a text to any of my messages to turn it into a status message.')
        status_message_id[0] = True
    if type(status_message_id[0]) is bool and message.reply_to_message:
        if message.reply_to_message.from_user.id == 5063051229:
            status_message_id[0] = message.reply_to_message.message_id


def update_status_message(bot: TeleBot, status_message_id: list, previous_status: list):
    if type(status_message_id[0]) is not bool:
        new_status = datetime.now().strftime('%d.%m.%Y %H:%M(%S)')
        if new_status != previous_status[0]:
            bot.edit_message_text(new_status, STATUS_CHANNEL, status_message_id[0])
            previous_status[0] = new_status


def show_current_settings(bot: TeleBot, message):
    bot.send_message(message.chat.id, 'Current settings:')
    settings = open(USER_CONFIG_PATH, 'r')
    bot.send_message(message.chat.id, settings.read())


def update_settings(bot: TeleBot, message, user_config):
    text = message.text.split('\n')
    failures = []
    for line in text:
        if len(line.split(' ')) < 3:
            failures.append(line)
            continue

        user_config.read(USER_CONFIG_PATH)
        section, variable = line.split(' ')[:2]
        value = ' '.join(line.split(' ')[2:])
        if ' ' in section or ' ' in variable or section not in user_config.sections():
            failures.append(line)
            continue

        user_config[section][variable] = value
        with open(USER_CONFIG_PATH, 'w') as configfile:
            user_config.write(configfile)

    failures = '\n'.join(failures)
    if failures:
        bot.send_message(message.chat.id, 'These commands cannot be processed:')
        bot.send_message(message.chat.id, failures)
    else:
        bot.send_message(message.chat.id, 'The settings have been successfully changed')


def purchase_handler(bot, message):
    failures = af.add_purchase(message.text)
    if failures:
        bot.send_message(message.chat.id, 'Oops... these costs could not be processed:')
        bot.send_message(message.chat.id, '\n'.join(failures))
    else:
        bot.send_message(message.chat.id, 'Like clockwork! Anything else?')


def show_costs_stats(bot, chat_id, section, user_config, config_path=USER_CONFIG_PATH):
    user_config.read(config_path)

    period = user_config.get(section, 'period')
    pieces = user_config.getint(section, 'pieces')
    head = user_config.getint(section, 'head')

    show_report = user_config.getboolean(section, 'show_report')
    show_cpd = user_config.getboolean(section, 'show_cpd')
    show_percentage = user_config.getboolean(section, 'show_percentage')
    show_products = user_config.getboolean(section, 'show_products')
    show_prices = user_config.getboolean(section, 'show_sum')
    show_pie = user_config.getboolean(section, 'show_pie')
    show_total = user_config.getboolean(section, 'show_total')

    if show_report is False and show_pie is False:
        bot.send_message(chat_id, 'You don\'t get any statistics at the moment. Update the settings for the '
                                  'information you want to receive')
        return
    if (show_cpd, show_percentage, show_products, show_prices, show_total) == (False, False, False, False, False):
        show_report = False

    period, plot, stats, total, days = af.stats_from_costs_in_the_period(af.COSTS_HISTORY_PATH, period, pieces, head)

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
    bot.send_message(chat_id, 'Expenses for the period\n' + period)
    if show_pie is True:
        bot.send_photo(chat_id, plot)

    if show_report is True and show_total is True:
        bot.send_message(chat_id, lines + '\n\nTotal: ' + str(total) +
                         ' (' + str(round(total / days, 2)) + ' per day)')
    elif show_report is True and show_total is False:
        bot.send_message(chat_id, lines)
