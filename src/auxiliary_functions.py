import pandas as pd
from configparser import ConfigParser
from datetime import date, timedelta
from time import strptime
from copy import copy
from PIL import Image
from matplotlib import pyplot as plt
from config import COSTS_HISTORY_PATH, BOT_PATH, PASSWORDS, DIET_CONFIG_PATH, PRODUCTS_DATABASE_PATH, \
    USER_CONFIG_PATH, GUIDES_PATH
from colour import Color
from os import mkdir
from os.path import exists
from cryptography.fernet import Fernet
from enchant.utils import levenshtein
from data.Databases.messages import PHRASES, WORDS, SUPPORTED_LANGUAGES

from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

HEADERS = ['date', 'price', 'product']

# CPFC_PRESETS = {'weight-loss': {'calories': 2000, 'proteins': 90, 'fats': 60, 'carbohydrates': 250}}


# SECURITY block
def encrypt(filepath, password: str):
    f = Fernet(password)
    with open(filepath, 'r', encoding='utf-8') as file:
        # прочитать все данные файла
        file_data = file.read()

    # зашифровать данные
    encrypted_data = f.encrypt(file_data.encode('utf-8'))
    # записать зашифрованный файл
    with open(filepath, 'wb') as file:
        file.write(encrypted_data)


def decrypt(filepath, password):
    f = Fernet(password)
    with open(filepath, 'rb') as file:
        # читать зашифрованные данные
        encrypted_data = file.read()

    # расшифровать данные
    decrypted_data = f.decrypt(encrypted_data)
    # записать оригинальный файл
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(decrypted_data.decode('utf-8'))


def generate_password(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if str(user_id) not in PASSWORDS:
        password = Fernet.generate_key().decode('utf-8')
        PASSWORDS[str(user_id)] = str(password)
        # print('lol')
        bot.send_message(chat_id, get_phrase(user_id, 38))
        bot.send_message(chat_id, password)
        bot.send_message(chat_id, get_phrase(user_id, 39))


def ensure_path(path):
    try:
        mkdir(path)
    except FileExistsError:
        pass


# COSTS block
def add_purchase(purchase: str, user_id):
    """ Updates costs history.
    Args:
        purchase (str): purchase as several lines 'price product\n...' or 'price\n...'.
        user_id: user ID
    Returns:
        list[str]: list of wrong purchases.
    """

    # reading/creating costs history
    try:
        costs_history = pd.read_csv(COSTS_HISTORY_PATH.format(user_id))
    except FileNotFoundError:
        costs_history = pd.DataFrame(columns=HEADERS)

    failed = []

    purchases = purchase.split('\n')
    for purchase in purchases:
        if split_purchase(purchase) is None:
            failed.append(purchase)
            continue

        purchase = pd.DataFrame([split_purchase(purchase)], columns=HEADERS)
        costs_history = pd.concat([purchase, costs_history], ignore_index=True)

    costs_history.to_csv(COSTS_HISTORY_PATH.format(user_id), index=False)
    return failed


def split_purchase(purchase: str):
    """ Converts the entered purchase as a string to a list and adds the operation time.
    Args:
        purchase (str): purchase as one line 'price product' or 'price'.
    Returns:
        list[str, float, str]|None: ['date', price, 'product'].
            None if the price is incorrect (not number / missing).
    """

    timestamp = dd_mm_yyyy(date.today())  # DD.MM.YYYY

    if ' ' not in purchase:  # если подали предположительно только цену
        purchase = purchase.replace(',', '.')

        try:
            price = float(purchase)
        except ValueError:
            return

        return [timestamp, price, '']

    price = purchase[:purchase.index(' ')]
    price = price.replace(',', '.')
    product = purchase[purchase.index(' ') + 1:]
    product = product.lower()
    product = product[0].upper() + product[1:]

    try:
        price = float(price)
    except ValueError:
        return

    return [timestamp, price, product]


def stats_from_costs_in_the_period(entries_file_path, user_id, period='all-time', pieces=10, head=10):
    """
    Args:
        entries_file_path: datafile path
        user_id (int): user ID
        period (str|list[str, str]): [start time; end time], each time is 'DD.MM.YYYY'.
        pieces (int): the number of pie plot pieces.
        head (int): the number of things that cost the most
    """

    def percentage(number1, number2, precision=1):
        """ Returns how many percent of number1 is number2.
        The precision parameter specifies the maximum number of digits after the decimal point. """
        return round(number2 * 100 / number1, precision)

    data = entries_in_the_period(entries_file_path, period=period)  # данные о расходах

    prices = []
    percents = []
    products = list(data['product'].unique())

    for product in products:
        prices.append(round(data['price'][data['product'] == product].sum(), 2))
    total = sum(prices)  # все потраченные деньги за выбранное время
    for price in prices:
        percents.append(percentage(total, price))

    simultaneous = zip(percents, products, prices)
    simultaneous = sorted(simultaneous, key=lambda tup: tup[0])
    percents = [x[0] for x in simultaneous]
    products = [x[1] for x in simultaneous]
    prices = [x[2] for x in simultaneous]

    percents.reverse()
    products.reverse()
    prices.reverse()

    red = Color("Red")
    colors = list(red.range_to(Color("Green"), pieces + 1))
    for i in range(len(colors)):
        colors[i].set_luminance(0.75)
    colors = [color.get_hex_l() for color in colors]

    plt.pie(prices[:pieces] + [sum(prices[pieces:])], labels=products[:pieces] + [get_word(user_id, 'Other')],
            colors=colors, autopct='%1.1f%%', pctdistance=0.85, startangle=90,
            wedgeprops={"edgecolor": "k", 'linewidth': 1, 'linestyle': 'solid', 'antialiased': True})
    centre_circle = plt.Circle((0, 0), 0.70, fc='white', ec='black', linestyle='solid')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    fig = plt.gcf()
    plot = fig2img(fig)

    plt.cla()
    plt.clf()
    plt.close()

    stats = []
    for i in range(len(products)):
        stats.append([percents[i], ' - ' + products[i] + ' - ' + str(round(prices[i], 2))])
    stats.sort(key=lambda x: x[0])

    # временной период для которого произведен рассчет
    period = dd_mm_yyyy(strpdate(data['date'][len(data['date']) - 1], '%d.%m.%Y')) + ' - ' + dd_mm_yyyy(date.today())
    # кол-во дней во временном периоде для которого произведен рассчет
    days = (date.today() - strpdate(data['date'][len(data['date']) - 1], '%d.%m.%Y')).days

    return period, plot, [[a, b, c] for a, b, c in zip(percents, products, prices)][:head], round(total, 2), days


def entries_in_the_period(entries_file_path, period='all-time'):
    """
    Returns a dataframe of entries in a given time period with an error equal to the maximum time
    difference between the entries. For example, if a entries was made a year ago and no entries
    were made after it, the preset 'one-week' will still count that entries (as well as all records dated like it).
    Period presets:
        'all-time', 'one-week', 'two-weeks', 'three-weeks',
        'one-month', 'two-months', 'three-months', 'one-year'.
    Args:
        period (str|list[str, str]): [start time; end time], each time is 'DD.MM.YYYY'.
        entries_file_path (str): datafile path
    Returns:
        pd.DataFrame|None: Entries in the period as pd.DataFrame.
            None if entries file does't exist or the period is not set correctly.
    """

    try:
        entries = pd.read_csv(entries_file_path)
    except FileNotFoundError:
        return

    # For presets. 'all-time' preset returns all entries in file.
    # Others presets creates time period and returns entries_in_the_period(entries_file_path, [time period])
    if type(period) is str:

        if period == 'all-time':
            return entries

        if period == 'one-week':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=1)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'two-weeks':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=2)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'three-weeks':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=3)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'one-month':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=4)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'two-months':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=8)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'three-months':
            period = [dd_mm_yyyy(date.today() - timedelta(weeks=12)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

        if period == 'one-year':
            period = [dd_mm_yyyy(date.today() - timedelta(days=365)), dd_mm_yyyy(date.today())]
            return entries_in_the_period(entries_file_path, period)

    # For time period as list [start time, end time]
    if type(period) is list:

        if type(period[0]) is not str or type(period[1]) is not str:
            return

        time = copy(entries['date'])
        for i in range(len(time)):
            time[i] = strptime(time[i], '%d.%m.%Y').tm_yday

        # looks for the index of the date that is closer to the lower boundary of the period
        min_index, value = min(enumerate(time),
                               key=lambda x: abs(x[1] - strptime(period[0], '%d.%m.%Y').tm_yday))

        max_index = max([i for i, d in enumerate(time) if d == value])

        # looks for the index of the date that is closer to the upper boundary of the period
        min_index, value = min(enumerate(time),
                               key=lambda x: abs(x[1] - strptime(period[1], '%d.%m.%Y').tm_yday))

        return entries[min_index:max_index + 1]


# DIET block
def new_products_handler(bot: TeleBot, message: Message, products_type):
    assert products_type in ['allowed', 'each-meal'], ValueError(f'Wrong products type: "{str(products_type)}"')
    user_id = message.from_user.id

    cpfc = pd.read_csv(PRODUCTS_DATABASE_PATH)
    products = list(cpfc['product'])
    new_products = message.text.split('\n')
    failures = []

    def _levenshtein(products_database, product):
        similar = []
        leven_distances = [(products_database[i], min([levenshtein(product.lower(), word)
                                                       for word in products_database[i].lower().split()]))
                           for i in range(len(products_database))]
        leven_distances.sort(key=lambda x: x[1])

        similar.append((product, '\n- '.join([product for product, distance in leven_distances[:3]])))
        return similar

    if products_type == 'allowed':
        for new_product in new_products:
            if new_product in products:
                add_product(user_id, new_product, products_type)
            else:
                failures += _levenshtein(products, new_product)

    if products_type == 'each-meal':
        new_products = [(' '.join(product_grams.split()[:-1]), product_grams.split()[-1])
                        for product_grams in new_products]
        for new_product, grams in new_products:
            if new_product in products:
                add_product(user_id, ' '.join([new_product, grams]), products_type)

            else:
                failures += _levenshtein(products, new_product)

    keyboard = inline_keyboard([get_phrase(user_id, 33).format(get_word(user_id, products_type))],
                               callback_data=[f'Show {products_type} products'])
    if failures:
        failures = get_phrase(user_id, 36) + '\n\n'.join([get_phrase(user_id, 35) + f' "{product}":\n- ' +
                                                          similars for product, similars in failures])
        bot.send_message(user_id, failures, reply_markup=keyboard)
    else:
        bot.send_message(user_id, get_phrase(user_id, 37), reply_markup=keyboard)


def add_product(user_id, new_product, products_type):
    assert products_type in ['allowed', 'each-meal'], ValueError(f'Wrong products type: "{str(products_type)}"')

    config, _ = read_config(DIET_CONFIG_PATH, user_id)
    if products_type == 'allowed':
        products = config['Diet']['products'] + ',' + new_product
        update_config(DIET_CONFIG_PATH, user_id, 'Diet products ' + products)
    elif products_type == 'each-meal':
        products = config['Diet']['each_meal_products'] + ',' + new_product
        update_config(DIET_CONFIG_PATH, user_id, 'Diet each_meal_products ' + products)


def generate_diet(user_id):
    # получаем все продукты из конфигурационного файла, наименования которых присутсвуют в базе данных КБЖУ продуктов
    config, _ = read_config(DIET_CONFIG_PATH, user_id)
    cpfc = pd.read_csv(PRODUCTS_DATABASE_PATH)

    products = [product for product in config['Diet']['products'].split(',')
                if product in list(cpfc['product'])]
    if not products:
        return
    each_meal = []  # продукты которые обязательно должны быть включены в рацион и их грамовки
    for product_grams in config['Diet']['each_meal_products'].split(','):
        if product_grams != '':
            product = ' '.join(product_grams.split()[:-1])
            grams = int(product_grams.split()[-1])
            if product in list(cpfc['product']):
                each_meal.append((product, grams))
                if product not in products:
                    products.append(product)

    days = int(config['Diet']['days'])  # кол-во дней для которых генерится рацион
    meals = int(config['Diet']['meals'])  # кол-во приемов пищи в день

    min_of_calories = value2int(config['Advanced']['calories'])
    min_of_proteins = value2int(config['Advanced']['proteins'])
    min_of_fats = value2int(config['Advanced']['fats'])
    min_of_carbs = value2int(config['Advanced']['carbohydrates'])

    # словарь содержит дни, содержащие приемы пищи, которые в свою очередь содержат наименования блюд
    diet = {i: {j: {} for j in range(1, meals + 1)} for i in range(1, days + 1)}
    grams_of_product = {product: 0 for product in products}  # дневные граммовки каждого из продуктов

    calories = 0  # килокалории
    proteins = 0  # белки
    fats = 0  # жиры
    carbohydrates = 0  # углеводы

    for product, grams in each_meal:
        # рацион будет составляться отталкиваясь от того какие продукты ообязательно должны присутствовать
        info = cpfc[cpfc['product'] == product]
        calories += int(info['calories'])
        proteins += int(info['proteins'])
        fats += int(info['fats'])
        carbohydrates += int(info['carbohydrates'])
        grams_of_product[product] += grams

    print(products)
    print(grams_of_product)
    # gg
    return diet


# CONFIGS block
def read_config(config_path: str, user_id):
    """ Return config as ConfigParser obj. and content as string (content of the config). """
    config = ConfigParser()

    decrypt(config_path.format(user_id), PASSWORDS[str(user_id)])
    try:
        file = open(config_path.format(user_id), 'r', encoding='utf-8')
        content = file.read()
        file.close()
        config.read(config_path.format(user_id), encoding='utf-8')
    except Exception as e:
        encrypt(config_path.format(user_id), PASSWORDS[str(user_id)])
        raise e
    encrypt(config_path.format(user_id), PASSWORDS[str(user_id)])

    return config, content


def update_config(config_path: str, user_id, commands: str):
    config = ConfigParser()

    decrypt(config_path.format(user_id), PASSWORDS[str(user_id)])
    try:
        text = commands.split('\n')
        failures = []
        for line in text:
            if len(line.split(' ')) < 3:
                failures.append(line)
                continue

            config.read(config_path.format(user_id), encoding='utf-8')
            section, variable = line.split(' ')[:2]
            value = ' '.join(line.split(' ')[2:])
            if ' ' in section or ' ' in variable or section not in config.sections():
                failures.append(line)
                continue

            config[section][variable] = value
            with open(config_path.format(user_id), 'w', encoding='utf-8') as configfile:
                config.write(configfile)
    except Exception as e:
        encrypt(config_path.format(user_id), PASSWORDS[str(user_id)])
        raise e
    encrypt(config_path.format(user_id), PASSWORDS[str(user_id)])

    return failures


def load_default_config(config_path: str, user_id):
    default_config_path = config_path.split('/')
    default_config_path = BOT_PATH + '/data/Defaults/default_' + default_config_path[-1]

    default = open(default_config_path, 'r', encoding='utf-8')
    default_settings = default.read()
    default.close()
    user_config = open(config_path.format(user_id), 'w', encoding='utf-8')
    user_config.write(default_settings)
    user_config.close()
    encrypt(config_path.format(user_id), PASSWORDS[str(user_id)])


# LANGUAGE block
def get_phrase(user_id, message_id):
    language = define_language(user_id)
    return PHRASES[language][message_id]


def get_word(user_id, word):
    language = define_language(user_id)
    return WORDS[word][language]


def define_language(user_id):
    if str(user_id) in PASSWORDS.keys() and exists(USER_CONFIG_PATH.format(user_id)):
        config, _ = read_config(USER_CONFIG_PATH, user_id)
        language = config['General']['language']
        if language not in SUPPORTED_LANGUAGES:
            language = 'EN'
    else:
        language = 'EN'

    return language


def check_for_keywords(bot: TeleBot, user_id, text):
    check_language(bot, user_id)

    config, _ = read_config(USER_CONFIG_PATH, user_id)
    language = config['General']['language']
    for keyword in WORDS.keys():
        if text == WORDS[keyword][language]:
            return keyword


def check_language(bot: TeleBot, user_id):
    config, _ = read_config(USER_CONFIG_PATH, user_id)
    language = config['General']['language']
    if language not in SUPPORTED_LANGUAGES:
        keyboard = inline_keyboard(['Change language'], callback_data=['Set language'])
        bot.send_message(user_id, 'A language that is not supported is set in the settings. Please, change language.',
                         reply_markup=keyboard)
        raise ValueError('Wrong language')


# GUIDES block
def send_user_guide(bot: TeleBot, user_id, section=None):
    guides = check_for_guides(['Full', 'Settings', 'Costs', 'Diet', 'To-do'])
    # each guide name is "User guide [type] [language].pdf"
    language = define_language(user_id)

    def _send_full_guide():
        if guides['Full'][language]:
            bot.send_document(user_id, open(GUIDES_PATH + f'/User guide [Full] [{language}].pdf', 'rb'))
        elif guides['Full']['EN']:
            bot.send_document(user_id, open(GUIDES_PATH + '/User guide [Full] [EN].pdf', 'rb'))
        else:
            for lang in guides['Full'].keys():
                if guides['Full'][lang]:
                    bot.send_document(user_id, open(GUIDES_PATH + f'/User guide [Full] [{lang}].pdf', 'rb'))

    def _get_guide_name(guide_type):
        if True not in guides[guide_type].values():
            return []
        if guides[guide_type][language]:
            return [f'/User guide [{guide_type}] [{language}].pdf']
        elif guides[guide_type]['EN']:
            return [f'/User guide [{guide_type}] [EN].pdf']
        else:
            names = []
            for lang in guides[guide_type].keys():
                if guides[guide_type][lang]:
                    names.append(f'/User guide [{guide_type}] [{lang}].pdf')

    if section is None:
        bot.send_message(user_id, get_phrase(user_id, 7))
        _send_full_guide()
    elif section in ['Settings', 'Costs', 'Diet', 'To-do']:
        if _get_guide_name(section):
            for guide in _get_guide_name(section):
                bot.send_message(user_id, get_phrase(user_id, 8))

                guide = open(GUIDES_PATH + guide, 'rb')
                bot.send_document(user_id, guide)
            keyboard = inline_keyboard([get_phrase(user_id, 46)], callback_data=['Send full user guides'])
            bot.send_message(user_id, get_phrase(user_id, 9),
                             reply_markup=keyboard)

        else:
            bot.send_message(user_id, get_phrase(user_id, 10))
            _send_full_guide()


def check_for_guides(guide_types: list):
    report = {guide_type: {} for guide_type in guide_types}
    for guide_type in guide_types:
        for language in SUPPORTED_LANGUAGES:
            if exists(GUIDES_PATH + f'/User guide [{guide_type}] [{language}].pdf'):
                report[guide_type][language] = True
            else:
                report[guide_type][language] = False

    return report


# OTHER block
def inline_keyboard(text, rows_lengths=None, **kwargs):
    """ Создает инлайновую клавиатуру с кнопками. Можно выбрать кол-во кнопок в каждой из строк,
    а также присваивать кнопкам любые атрибуты, передавая соответствующий список в параметр kwargs.

    Пример:
    keyboard_maker(['General', 'Costs', 'Diet', 'To-do'], rows_lengths=[1, 2, 1],
                   callback_data=['General', 'Costs', 'Diet', 'To-do'])

    создаст инлайновую клавиатуру в первой строке которой будет кнопка General, во второй Costs и Diet,
    а в третьей To-do. Каждая из кнопок будет иметь одноименное значение параметра callback_data.

    """

    for kwarg in kwargs.values():
        assert len(kwarg) == len(text), ValueError('All arrays must have the same length.')

    buttons = []
    keyboard = InlineKeyboardMarkup()
    for i in range(len(text)):
        button = InlineKeyboardButton(text[i])
        for key in kwargs.keys():
            button.__setattr__(key, kwargs[key][i])
        buttons.append(button)

    if isinstance(rows_lengths, int):
        assert rows_lengths > 0, ValueError('Parameter rows_lengths must be greater than 0.')
        for i in range(0, len(buttons), rows_lengths):
            row = tuple(buttons[i:i + rows_lengths])
            keyboard.add(*row, row_width=rows_lengths)
    elif isinstance(rows_lengths, list) or isinstance(rows_lengths, tuple):
        i, j = 0, 0
        while i < len(buttons):
            rows_length = rows_lengths[j]
            row = tuple(buttons[i:i + rows_length])
            keyboard.add(*row, row_width=rows_length)

            i += rows_length
            j += 1
    else:
        buttons = tuple(buttons)
        keyboard.add(*buttons)

    return keyboard


def fig2img(fig, dpi=500):
    """ Convert a Matplotlib figure to an Image, crop and return it.
    Args:
        fig (matplotlib.figure.Figure): figure
        dpi (int): dots per inch in output image
    Returns:
        Image.Image: opened Image object
    """

    import io
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi)  # dpi - dots per inch
    buf.seek(0)
    img = Image.open(buf)
    w, h = img.size
    img = img.crop((round(0.15 * w), round(0.1 * h), w - round(0.15 * w) + 50, h - round(0.1 * h)))
    return img


def dd_mm_yyyy(date_object: date):
    """ Returns date as "DD.MM.YYYY". """
    return "%02d.%02d.%04d" % (date_object.day, date_object.month, date_object.year)


def strpdate(string: str, formatting: str):
    """ strpdate(str_date, formatting) -> date """
    time_from_str = strptime(string, formatting)
    return date(time_from_str.tm_year, time_from_str.tm_mon, time_from_str.tm_mday)


def value2int(value):
    """ value --> float --> int """
    try:
        return int(float(value))
    except ValueError:
        return None


if __name__ == '__main__':
    print(generate_diet(758913011))
