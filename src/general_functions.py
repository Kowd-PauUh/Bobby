from datetime import datetime
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton
from telebot.apihelper import ApiTelegramException
from configparser import ConfigParser
from os.path import exists

from config import GENERAL_CONFIG_PATH, USER_CONFIG_PATH, STATUS_CHANNEL, BOT_PATH, PASSWORDS, COSTS_HISTORY_PATH, \
    DIET_CONFIG_PATH, COSTS_CONFIG_PATH, TODO_CONFIG_PATH, SECTIONS
from data.Databases.messages import PHRASES
import src.auxiliary_functions as af

GENERAL_CONFIG = ConfigParser()
SETTINGS_SECTIONS_PATHS = {'General': USER_CONFIG_PATH,
                           'Costs': COSTS_CONFIG_PATH,
                           'Diet': DIET_CONFIG_PATH,
                           'To-do': TODO_CONFIG_PATH,
                           'Settings': USER_CONFIG_PATH}


# BRANCHING block
def branching(bot: TeleBot, message: Message, user_id):
    section = af.check_for_keywords(bot, user_id, message.text)
    af.update_config(USER_CONFIG_PATH, user_id, f'General section {section}')
    af.update_config(SETTINGS_SECTIONS_PATHS[section], user_id, 'DontChangeIt action None')
    config, _ = af.read_config(USER_CONFIG_PATH, user_id)

    if section == 'Settings':
        settings_section = config['DontChangeIt']['settings_section']
        buttons_names = [af.get_word(user_id, word) for word in ['General', 'Costs', 'Diet', 'To-do']]
        buttons_names.insert(1, 'Language')
        keyboard = af.inline_keyboard(buttons_names, rows_lengths=[2, 3],
                                      callback_data=['General', 'Set language', 'Costs', 'Diet', 'To-do'])
        text = af.get_phrase(user_id, 3) + af.get_phrase(user_id, 12).format(af.get_word(user_id, settings_section))
        bot.send_message(user_id, text, reply_markup=keyboard)

    elif section == 'Costs':
        buttons_names = [af.get_word(user_id, word) for word in ['Guide', 'Stats']]
        keyboard = af.inline_keyboard(buttons_names, callback_data=['Send user guide', 'Costs Stats'])
        text = af.get_phrase(user_id, 4) + af.get_phrase(user_id, 13)
        bot.send_message(user_id, text, reply_markup=keyboard)

    elif section == 'Diet':
        buttons_names = [af.get_word(user_id, word) for word in ['Guide', 'Generate', 'Stats', 'Products']]
        keyboard = af.inline_keyboard(buttons_names, rows_lengths=2,
                                      callback_data=['Send user guide', 'Generate diet', 'Diet Stats', 'Products'])
        text = af.get_phrase(user_id, 5) + af.get_phrase(user_id, 14)
        bot.send_message(user_id, text, reply_markup=keyboard)

    elif section == 'To-do':
        buttons_names = [af.get_word(user_id, word) for word in ['Guide', 'Reminder', 'To-do list']]
        keyboard = af.inline_keyboard(buttons_names, rows_lengths=[3],
                                      callback_data=['Send user guide', 'Reminder', 'To-do list'])
        text = af.get_phrase(user_id, 6) + af.get_phrase(user_id, 15)
        bot.send_message(user_id, text, reply_markup=keyboard)


def keyboard_replies_manager(bot: TeleBot, callback: CallbackQuery):
    user_id = callback.from_user.id
    config, _ = af.read_config(USER_CONFIG_PATH, user_id)
    section = config['General']['section']

    if callback.data == 'Send user guide':
        af.send_user_guide(bot, user_id, section)
        return
    if callback.data == 'Send full user guides':
        af.send_user_guide(bot, user_id)
        return
    if callback.data == 'Set language':
        keyboard = af.inline_keyboard(list(PHRASES.keys()), callback_data=list(PHRASES.keys()))
        bot.send_message(user_id, 'Select language.', reply_markup=keyboard)
        return
    if callback.data in PHRASES.keys():
        af.update_config(USER_CONFIG_PATH, user_id, f'General language {callback.data}')
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for section in SECTIONS:
            keyboard.add(KeyboardButton(af.get_word(user_id, section)))
        bot.send_message(user_id, af.get_phrase(user_id, 43).format(af.get_word(user_id, callback.data)),
                         reply_markup=keyboard)
        return

    if section == 'Settings':
        if callback.data in ['General', 'Costs', 'Diet', 'To-do']:
            af.update_config(USER_CONFIG_PATH, user_id, f'DontChangeIt settings_section {callback.data}')
            keyboard = af.inline_keyboard([af.get_word(user_id, 'Guide'), af.get_phrase(user_id, 11)],
                                          callback_data=['Send user guide', 'Show settings'])

            text = af.get_phrase(user_id, 3) + af.get_phrase(user_id, 16).format(af.get_word(user_id, callback.data))
            bot.edit_message_text(text, user_id, callback.message.id, callback.inline_message_id)
            bot.edit_message_reply_markup(user_id, callback.message.id, callback.inline_message_id,
                                          reply_markup=keyboard)
        elif callback.data == 'Show settings':
            settings_section = config['DontChangeIt']['settings_section']
            show_current_settings(bot, user_id, settings_section)

    elif section == 'Costs':
        if callback.data == 'Costs Stats':
            show_costs_stats(bot, user_id, 'Stats')

    elif section == 'Diet':
        if callback.data == 'Generate diet':
            bot.send_message(user_id, af.get_phrase(user_id, 32))
        elif callback.data == 'Diet Stats':
            bot.send_message(user_id, af.get_phrase(user_id, 32))
        elif callback.data == 'Products':
            buttons_names = [af.get_phrase(user_id, 31), af.get_phrase(user_id, 29), af.get_phrase(user_id, 30)]
            keyboard = af.inline_keyboard(buttons_names, rows_lengths=[1, 1, 1],
                                          callback_data=['Show current products',
                                                         'Modify allowed products',
                                                         'Modify each-meal products'])
            bot.edit_message_text(af.get_phrase(user_id, 28), user_id, callback.message.id, callback.inline_message_id)
            bot.edit_message_reply_markup(user_id, callback.message.id, callback.inline_message_id,
                                          reply_markup=keyboard)
        elif callback.data in ['Modify allowed products', 'Modify each-meal products']:
            af.update_config(DIET_CONFIG_PATH, user_id, f'DontChangeIt action {callback.data}')
            products_type = callback.data.split()[1]
            keyboard = af.inline_keyboard([af.get_phrase(user_id, 33).format(af.get_word(user_id, products_type))],
                                          callback_data=[f'Show {products_type} products'])
            text = af.get_phrase(user_id, 5) + af.get_phrase(user_id, 34).format(af.get_word(user_id, products_type))
            bot.edit_message_text(text, user_id, callback.message.id, callback.inline_message_id)
            bot.edit_message_reply_markup(user_id, callback.message.id, callback.inline_message_id,
                                          reply_markup=keyboard)
        elif callback.data == 'Show current products':
            bot.delete_message(user_id, callback.message.id)
            show_current_products(bot, user_id, ['allowed', 'each-meal'])
        elif callback.data in ['Show allowed products', 'Show each-meal products']:
            products_type = callback.data.split()[1]
            show_current_products(bot, user_id, [products_type])

    elif section == 'To-do':
        bot.send_message(user_id, af.get_phrase(user_id, 32))


# SECURITY block
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


def access_check(bot: TeleBot, user_id):
    GENERAL_CONFIG.read(GENERAL_CONFIG_PATH)
    users_with_access = GENERAL_CONFIG['General']['USERS_WITH_ACCESS'].split(',')
    if str(user_id) not in users_with_access:
        bot.send_message(user_id, 'You do not have access to the bot.')
        raise ValueError('Attempted access by a user who does not have access. User ID: ' + str(user_id))


def check_user_files(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    flag = False

    # если у юзера нет своей папки, создать все нужные папки и файлы и пароль для юзера
    if not exists(BOT_PATH + '/data/Users/{}'.format(user_id)):
        flag = True
        af.generate_password(bot, message)  # создать пароль для юзера

        af.ensure_path(BOT_PATH + '/data/Users/{}'.format(user_id))
        af.ensure_path(BOT_PATH + '/data/Users/{}/costs'.format(user_id))
        af.ensure_path(BOT_PATH + '/data/Users/{}/diet'.format(user_id))
        af.ensure_path(BOT_PATH + '/data/Users/{}/todo'.format(user_id))

    # когда папка сществует, проверить наличие всех файлов
    password_check(bot, message)
    general_config = ConfigParser()
    general_config.read(GENERAL_CONFIG_PATH)
    paths_names = general_config['Files']['paths_names']
    for path_name in paths_names.split(','):
        filepath = (BOT_PATH + general_config['Files'][path_name]).format(user_id)
        if not exists(filepath):
            default_file = BOT_PATH + '/data/Defaults/default_' + filepath.split('/')[-1]
            default_file = open(default_file, 'r')
            default_content = default_file.read()
            file = open(filepath, 'w')
            file.write(default_content)
            default_file.close()
            file.close()

            af.encrypt(filepath, PASSWORDS[str(user_id)])

    if flag:
        af.send_user_guide(bot, user_id)

        keyboard = af.inline_keyboard(['Change language'], callback_data=['Set language'])
        bot.send_message(user_id, 'You can start by choosing the language in which you want to communicate with me. '
                                  'Later you can change it in the settings.', reply_markup=keyboard)


# STATUS UPDATING block
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


# SETTINGS block
def show_current_settings(bot: TeleBot, user_id, settings_section: str):
    _, content = af.read_config(SETTINGS_SECTIONS_PATHS[settings_section], user_id)

    if content:
        bot.send_message(user_id, af.get_phrase(user_id, 17).format(af.get_word(user_id, settings_section)))
        bot.send_message(user_id, content)
    else:
        bot.send_message(user_id, af.get_phrase(user_id, 18))


def update_settings(bot: TeleBot, message: Message, settings_section: str):
    user_id = message.from_user.id
    failures = af.update_config(SETTINGS_SECTIONS_PATHS[settings_section], user_id, message.text)

    show_settings_button = InlineKeyboardButton('Show settings', callback_data='Show settings')
    keyboard = InlineKeyboardMarkup().add(show_settings_button)

    if failures:
        failures = '\n'.join(failures)
        bot.send_message(message.chat.id, 'These commands cannot be processed:')
        bot.send_message(message.chat.id, failures, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'The settings have been successfully changed', reply_markup=keyboard)


def load_default_settings(bot: TeleBot, message: Message, settings_section: str):
    user_id = message.from_user.id
    config, _ = af.read_config(USER_CONFIG_PATH, user_id)
    if settings_section == 'General':
        section = config['General']['section']
        af.load_default_config(SETTINGS_SECTIONS_PATHS[settings_section], user_id)
        af.update_config(USER_CONFIG_PATH, user_id, f'General section {section}')
    else:
        af.load_default_config(SETTINGS_SECTIONS_PATHS[settings_section], user_id)

    show_settings_button = InlineKeyboardButton('Show new settings', callback_data='Show settings')
    keyboard = InlineKeyboardMarkup().add(show_settings_button)
    bot.send_message(message.chat.id, 'The settings have been successfully restored to their original state.',
                     reply_markup=keyboard)


# COSTS block
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
        bot.send_message(message.chat.id, af.get_phrase(user_id, 22))
        bot.send_message(message.chat.id, '\n'.join(failures))
    else:
        bot.send_message(message.chat.id, af.get_phrase(user_id, 23))


def show_costs_stats(bot: TeleBot, message_or_user_id, section):
    costs_config = ConfigParser()
    if isinstance(message_or_user_id, int):
        chat_id = message_or_user_id
        user_id = message_or_user_id
    else:
        assert isinstance(message_or_user_id, Message), \
            ValueError('Parameter message must be an isinstance of Message class or int (as user ID)')
        chat_id = message_or_user_id.chat.id
        user_id = message_or_user_id.from_user.id

    config_path = COSTS_CONFIG_PATH.format(user_id)
    af.decrypt(config_path, PASSWORDS[str(user_id)])
    try:
        costs_config.read(config_path)

        period = costs_config.get(section, 'period')
        pieces = costs_config.getint(section, 'pieces')
        head = costs_config.getint(section, 'head')

        show_report = costs_config.getboolean(section, 'show_report')
        show_cpd = costs_config.getboolean(section, 'show_cpd')
        show_percentage = costs_config.getboolean(section, 'show_percentage')
        show_products = costs_config.getboolean(section, 'show_products')
        show_prices = costs_config.getboolean(section, 'show_sum')
        show_pie = costs_config.getboolean(section, 'show_pie')
        show_total = costs_config.getboolean(section, 'show_total')
    except Exception as e:
        af.encrypt(config_path, PASSWORDS[str(user_id)])
        raise e
    af.encrypt(config_path, PASSWORDS[str(user_id)])

    if show_report is False and show_pie is False:
        bot.send_message(chat_id, af.get_phrase(user_id, 19))
        return
    if (show_cpd, show_percentage, show_products, show_prices, show_total) == (False, False, False, False, False):
        show_report = False

    af.decrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
    try:
        period, plot, stats, total, days = \
            af.stats_from_costs_in_the_period(COSTS_HISTORY_PATH.format(user_id), user_id, period, pieces, head)
    except (IndexError, TypeError):
        bot.send_message(chat_id, af.get_phrase(user_id, 20))
        af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])
        return
    af.encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])

    lines = []
    for percent, product, price in stats:
        cpd = (str(round(price / days, 2)) + af.get_word(user_id, '/day')) if show_cpd is True else ''
        percentage = str(percent) + '%' if show_percentage is True else ''
        product = product if show_products is True else ''
        price = str(price) if show_prices is True else ''
        line = [cpd, percentage, product, price]
        while '' in line:
            line.remove('')
        line = ' - '.join(line)
        lines.append(line)

    lines = '\n'.join(lines)
    bot.send_message(chat_id, af.get_phrase(user_id, 21) + period)
    if show_pie is True:
        bot.send_photo(chat_id, plot)

    if show_report is True and show_total is True:
        bot.send_message(chat_id, lines + af.get_word(user_id, '\n\nTotal: ') + str(total) +
                         ' (' + str(round(total / days, 2)) + af.get_word(user_id, ' per day)'))
    elif show_report is True and show_total is False:
        bot.send_message(chat_id, lines)


# DIET block
def show_current_products(bot: TeleBot, user_id, products_types: list):
    config, _ = af.read_config(DIET_CONFIG_PATH, user_id)

    if 'allowed' in products_types:
        products = config['Diet']['products'].replace(',', '\n')
        if products:
            bot.send_message(user_id, af.get_phrase(user_id, 24))
            bot.send_message(user_id, products)
        else:
            bot.send_message(user_id, af.get_phrase(user_id, 25))

    if 'each-meal' in products_types:
        products = config['Diet']['each_meal_products'].replace(',', '\n')
        if products:
            bot.send_message(user_id, af.get_phrase(user_id, 26))
            bot.send_message(user_id, products)
        else:
            bot.send_message(user_id, af.get_phrase(user_id, 27))

    if len(products_types) > 1:
        buttons_names = [af.get_phrase(user_id, 29), af.get_phrase(user_id, 30)]
        keyboard = af.inline_keyboard(buttons_names, rows_lengths=[1, 1],
                                      callback_data=['Modify allowed products', 'Modify each-meal products'])
        bot.send_message(user_id, af.get_phrase(user_id, 28),
                         reply_markup=keyboard)


def clear_products_list(bot: TeleBot, user_id, products_types):
    if 'allowed' in products_types:
        config, _ = af.read_config(DIET_CONFIG_PATH, user_id)
        config['Diet']['products'] = ''
        with open(DIET_CONFIG_PATH.format(user_id), 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        af.encrypt(DIET_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
        bot.send_message(user_id, af.get_phrase(user_id, 44))

    if 'each-meal' in products_types:
        config, _ = af.read_config(DIET_CONFIG_PATH, user_id)
        config['Diet']['each_meal_products'] = ''
        with open(DIET_CONFIG_PATH.format(user_id), 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        af.encrypt(DIET_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])
        bot.send_message(user_id, af.get_phrase(user_id, 45))
