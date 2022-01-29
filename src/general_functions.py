from datetime import datetime
from telebot import TeleBot
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from config import GENERAL_CONFIG_PATH, USER_CONFIG_PATH, STATUS_CHANNEL, BOT_PATH, PASSWORDS, COSTS_HISTORY_PATH
import src.auxiliary_functions as af
import configparser

GENERAL_CONFIG = configparser.ConfigParser()


def password_check(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if str(user_id) in PASSWORDS:
        return

    try:
        af.decrypt(USER_CONFIG_PATH.format(user_id), message.text)
        af.encrypt(USER_CONFIG_PATH.format(user_id), message.text)
    except Exception:
        bot.send_message(chat_id, 'Enter your password. This is wrong password.')
        raise ValueError('Wrong password')

    PASSWORDS[str(user_id)] = message.text
    bot.send_message(chat_id, 'Access granted!')
    raise ValueError('Access granted (exception to stop further functions)')


def access_check(bot: TeleBot, message: Message):
    GENERAL_CONFIG.read(GENERAL_CONFIG_PATH)
    users_with_access = GENERAL_CONFIG['General']['USERS_WITH_ACCESS'].split(',')
    user_id = message.from_user.id
    if str(user_id) not in users_with_access:
        bot.send_message(message.chat.id, 'You do not have access to the bot.')
        raise ValueError('Attempted access by a user who does not have access. User ID: ' + str(user_id))


def create_status_message(bot: TeleBot, message: Message, status_message_id: list):
    if message.chat.id != STATUS_CHANNEL:
        return

    GENERAL_CONFIG.read(GENERAL_CONFIG_PATH)
    if message.text == '/reset':
        bot.send_message(STATUS_CHANNEL, 'Reply with a text to any of my messages to turn it into a status message.')
        status_message_id[0] = True

    if type(status_message_id[0]) is bool and message.reply_to_message:
        if message.reply_to_message.from_user.id == bot.get_me().id:
            status_message_id[0] = message.reply_to_message.message_id
            update_status_message(bot, status_message_id, ['DD.MM.YYYY hh:mm(ss)'])
            bot.delete_message(message.chat.id, message.id)


def update_status_message(bot: TeleBot, status_message_id: list, previous_status: list):
    try:
        if status_message_id[0] is False:
            bot.send_message(STATUS_CHANNEL, 'Reply with a text to any of my messages '
                                             'to turn it into a status message.')
            status_message_id[0] = True

        try:
            if type(status_message_id[0]) is not bool:
                new_status = datetime.now().strftime('%d.%m.%Y %H:%M(%S)')
                if new_status != previous_status[0]:
                    bot.edit_message_text(new_status, STATUS_CHANNEL, status_message_id[0])
                    previous_status[0] = new_status
        except ApiTelegramException:
            bot.send_message(STATUS_CHANNEL, 'Reply with a text to any of my messages '
                                             'to turn it into a status message.')
            status_message_id[0] = True
    except ApiTelegramException:
        pass  # it means that the status chat ID is not set or is incorrect


def show_current_settings(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, 'Current settings:')

    af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
    try:
        settings = open(USER_CONFIG_PATH.format(user_id), 'r')
        bot.send_message(message.chat.id, settings.read())
    except Exception as e:
        af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
        raise e
    af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])


def update_settings(bot: TeleBot, message: Message, user_config):
    user_id = message.from_user.id
    af.decrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
    try:
        text = message.text.split('\n')
        failures = []
        for line in text:
            if len(line.split(' ')) < 3:
                failures.append(line)
                continue

            user_config.read(USER_CONFIG_PATH.format(user_id))
            section, variable = line.split(' ')[:2]
            value = ' '.join(line.split(' ')[2:])
            if ' ' in section or ' ' in variable or section not in user_config.sections():
                failures.append(line)
                continue

            user_config[section][variable] = value
            with open(USER_CONFIG_PATH.format(user_id), 'w') as configfile:
                user_config.write(configfile)
    except Exception as e:
        af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
        raise e
    af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])

    failures = '\n'.join(failures)
    if failures:
        bot.send_message(message.chat.id, 'These commands cannot be processed:')
        bot.send_message(message.chat.id, failures)
    else:
        bot.send_message(message.chat.id, 'The settings have been successfully changed')


def load_default_settings(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    default = open(BOT_PATH + '/data/Defaults/default_user_config.ini', 'r')
    default_settings = default.read()
    default.close()
    user_config = open(USER_CONFIG_PATH.format(user_id), 'w')
    user_config.write(default_settings)
    user_config.close()
    af.encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
    bot.send_message(message.chat.id, 'The settings have been successfully restored to their original state. '
                                      'You must again select a section.')


def purchase_handler(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    af.decrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
    try:
        failures = af.add_purchase(message.text, user_id)
    except Exception as e:
        af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
        raise e
    af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])

    if failures:
        bot.send_message(message.chat.id, 'Oops... these costs could not be processed:')
        bot.send_message(message.chat.id, '\n'.join(failures))
    else:
        bot.send_message(message.chat.id, 'Like clockwork! Anything else?')


def show_costs_stats(bot: TeleBot, message: Message, section, user_config):
    chat_id = message.chat.id
    user_id = message.from_user.id
    config_path = USER_CONFIG_PATH.format(user_id)
    af.decrypt(config_path, PASSWORDS[str(user_id)])
    try:
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
    except Exception as e:
        af.encrypt(config_path, PASSWORDS[str(user_id)])
        raise e
    af.encrypt(config_path, PASSWORDS[str(user_id)])

    if show_report is False and show_pie is False:
        bot.send_message(chat_id, 'You don\'t get any statistics at the moment. Update the settings for the '
                                  'information you want to receive')
        return
    if (show_cpd, show_percentage, show_products, show_prices, show_total) == (False, False, False, False, False):
        show_report = False

    af.decrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
    try:
        period, plot, stats, total, days = \
            af.stats_from_costs_in_the_period(COSTS_HISTORY_PATH.format(user_id), period, pieces, head)
    except (IndexError, TypeError):
        bot.send_message(chat_id, 'You don\'t have any statistics at the moment. Add some costs at first.')
        af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
        return
    af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])

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
