"""
Created by Ivan Danylenko
Date 22.12.2021
"""

from src.general_functions import *

import pandas as pd
from matplotlib import pyplot as plt
from datetime import date
from config import COSTS_HISTORY_PATH
from colour import Color

HEADERS = ['date', 'price', 'product']

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


def add_purchase(purchase: str):
    """ Updates costs history.

    Args:
        purchase (str): purchase as several lines 'price product\n...' or 'price\n...'.

    Returns:
        list[str]: list of wrong purchases.

    """

    # reading/creating costs history
    try:
        costs_history = pd.read_csv(COSTS_HISTORY_PATH)
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

    costs_history.to_csv(COSTS_HISTORY_PATH, index=False)
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
