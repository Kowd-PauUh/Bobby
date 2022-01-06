from functools import wraps
from datetime import date
from datetime import datetime as dt
from time import strptime
from telebot import TeleBot
from configparser import ConfigParser

from config import USERS_WITH_ACCESS
import src.general_functions as gf


CYCLIC_ACTIONS = {  # 'action-name': [[last date], [last time]]
    'show_weekly_costs_stats': [[date.today()], [dt.now().strftime('%H:%M')]],
    'show_monthly_costs_stats': [[date.today()], [dt.now().strftime('%H:%M')]],
    'send_good_morning': [[date.today()], [dt.now().strftime('%H:%M')]],
    # 'show-yearly-costs-stats': [[date.today()], [dt.now().strftime('%H:%M')]]
}


def planned_execution(period, description, last_usage):
    """ A decorator that limits the frequency of calls to the decorated function to once for a given period of time.

    Example of the usage:

    @planned_execution('week', [[date(2022, 1, 5)], ['00:00']])
    def new_cyclic_function(bot, user_config, config_path, description, **kwargs):
        pass

    Note:
        user_config, config_path and description parameters must be present in the decoded function,
        otherwise the decorator will raise an error. datetime parameter (list[int, str]): [day of period, daytime].
        Day of period: 1-7 for week, 1-31 for month, 1-365 for year. Daytime as 'HH:MM' (for example '23:59').

    Args:
        period (str): 'weekly' or 'month' or 'year'.
        description (str): name of variable in user_config.ini
        last_usage (list[list, list]): list that containing the datetime of the previous function call.

    """

    def _planned_execution(f):

        @wraps(f)
        def inner(**kwargs):
            user_config = kwargs['user_config']
            config_path = kwargs['config_path']

            user_config.read(config_path)
            datetimes = kwargs['user_config']['Cyclic'][description]
            datetimes = datetimes.split('/')

            for datetime in datetimes:
                day = int(datetime[:datetime.index(' ')])
                daytime = datetime[datetime.index(' ') + 1:]
                datetime = [day, daytime]

                # assertions
                try:
                    assert type(period) is str and period in ['week', 'month'] and type(datetime) is list \
                           and len(datetime) == 2 and type(datetime[0]) is int and type(datetime[1]) is str
                    if period == 'week':
                        assert 0 < datetime[0] < 8
                    elif period == 'month':
                        assert 0 < datetime[0] < 32
                except AssertionError:
                    continue

                # weekly cycle
                if period == 'week':
                    day_of_week, daytime = datetime
                    day_of_week -= 1
                    [last_day], [last_time] = last_usage

                    if date.today().weekday() == day_of_week and date.today() >= last_day:
                        if time_check(daytime, last_time, last_usage):
                            f(description=description, **kwargs)

                # monthly cycle
                if period == 'month':
                    day_of_month, daytime = datetime
                    [last_day], [last_time] = last_usage

                    if date.today().day == day_of_month and date.today() >= last_day:
                        if time_check(daytime, last_time, last_usage):
                            f(description=description, **kwargs)

        return inner

    return _planned_execution


def time_check(daytime, last_time, last_usage):
    """

    Check last_time < daytime <= time_now
    and change the datetime of last use (last_usage) if the inequality is true .

    Args:
        daytime (str): time as 'HH:MM'.
        last_time (str): time as 'HH:MM'.
        last_usage (list[list, list]): last usage of cyclic function. Read planned_execution().

    Returns:
        (bool): True if the inequality is true. False otherwise.

    """

    if strptime(last_time, '%H:%M') < strptime(daytime, '%H:%M') <= \
            strptime(dt.now().strftime('%H:%M'), '%H:%M'):
        last_usage[0] = [date.today()]
        if strptime(daytime, '%H:%M') > strptime(dt.now().strftime('%H:%M'), '%H:%M'):
            last_usage[1] = [daytime]
        else:
            last_usage[1] = [dt.now().strftime('%H:%M')]
        return True
    return False


@planned_execution(period='week', description='weekly_stats', last_usage=CYCLIC_ACTIONS['show_weekly_costs_stats'])
def show_weekly_costs_stats(bot: TeleBot, user_config: ConfigParser, config_path: str, description: str):
    """ In each function call all parameters should be entered as kwargs. """
    for user_id in USERS_WITH_ACCESS:
        bot.send_message(user_id, 'Weekly stats!')
        gf.show_costs_stats(bot, user_id, description, user_config, config_path)


@planned_execution(period='month', description='monthly_stats', last_usage=CYCLIC_ACTIONS['show_monthly_costs_stats'])
def show_monthly_costs_stats(bot: TeleBot, user_config: ConfigParser, config_path: str, description: str):
    """ In each function call all parameters should be entered as kwargs. """
    for user_id in USERS_WITH_ACCESS:
        bot.send_message(user_id, 'Monthly stats!')
        gf.show_costs_stats(bot, user_id, description, user_config, config_path)


@planned_execution(period='week', description='good_morning', last_usage=CYCLIC_ACTIONS['send_good_morning'])
def send_good_morning(bot: TeleBot, user_config: ConfigParser, config_path: str, description: str):
    """ In each function call all parameters should be entered as kwargs. """
    _ = user_config, config_path, description
    for user_id in USERS_WITH_ACCESS:
        bot.send_message(user_id, 'Good morning!')
