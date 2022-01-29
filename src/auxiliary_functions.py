import pandas as pd
from datetime import date, timedelta
from time import strptime
from copy import copy
from PIL import Image
from matplotlib import pyplot as plt
from config import COSTS_HISTORY_PATH, BOT_PATH, USER_CONFIG_PATH, PASSWORDS
from colour import Color
from os import mkdir
from os.path import exists
from cryptography.fernet import Fernet
from telebot import TeleBot
from telebot.types import Message

HEADERS = ['date', 'price', 'product']
GUIDES = ['RU']

PERIOD_PRESETS = [
    'all-time',
    'one-week',
    'two-weeks',
    'three-weeks',
    'one-month',
    'two-months',
    'three-months',
    'one-year'
]


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
        bot.send_message(chat_id, 'Your password for the bot is')
        bot.send_message(chat_id, password)
        bot.send_message(chat_id, 'Save it and do not show it to anyone, '
                                  'you will need it in case the bot is restarted.')


def ensure_path(path):
    try:
        mkdir(path)
    except FileExistsError:
        pass


def check_user_files(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # если у юзера нет своей папки, создать все нужные папки и файлы и пароль для юзера
    if not exists(BOT_PATH + '/data/{}'.format(user_id)):
        generate_password(bot, message)  # создать пароль для юзера
        if GUIDES:
            bot.send_message(chat_id, 'If this is the first time you have met me, '
                                      'you are encouraged to read one of this guides:')
            for guide_version in GUIDES:
                guide = open(BOT_PATH + f'/data/Guides/User guide [{guide_version}].pdf', 'rb')
                bot.send_document(chat_id, guide)

        ensure_path(BOT_PATH + '/data/{}'.format(user_id))
        ensure_path(BOT_PATH + '/data/{}/costs'.format(user_id))
        ensure_path(BOT_PATH + '/data/{}/diet'.format(user_id))
        ensure_path(BOT_PATH + '/data/{}/todo'.format(user_id))

        # создать файл конфигурационный файл с дефолтным содержанием
        default = open(BOT_PATH + '/data/Defaults/default_user_config.ini', 'r')
        default_settings = default.read()
        user_config = open(USER_CONFIG_PATH.format(user_id), 'w')
        user_config.write(default_settings)
        default.close()
        user_config.close()

        # зашифровать конфигурационный файл
        encrypt(USER_CONFIG_PATH.format(user_id), PASSWORDS[str(user_id)])

        # создать реестр расходов costs_history.csv
        costs_history = pd.DataFrame(columns=HEADERS)
        costs_history.to_csv(COSTS_HISTORY_PATH.format(user_id), index=False)

        # зашифровать реестр расходов
        encrypt(COSTS_HISTORY_PATH.format(user_id), PASSWORDS[str(user_id)])


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


def stats_from_costs_in_the_period(entries_file_path, period='all-time', pieces=10, head=10):
    """
    Args:
        entries_file_path: datafile path
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

    plt.pie(prices[:pieces] + [sum(prices[pieces:])], labels=products[:pieces] + ['Другое'], colors=colors,
            autopct='%1.1f%%', pctdistance=0.85, startangle=90,
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


def clear_history(entries_file_path):
    """ Clear all entries in file.
    Args:
        entries_file_path (str): datafile path.
    """

    try:
        entries = pd.read_csv(entries_file_path)
    except FileNotFoundError:
        return

    entries = pd.DataFrame(columns=entries.columns)
    entries.to_csv(entries_file_path, index=False)


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
