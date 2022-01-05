"""
Created by Ivan Danylenko
Date 04.01.2022
"""

import pandas as pd
from datetime import date, timedelta
from time import strptime
from copy import copy
from PIL import Image


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
