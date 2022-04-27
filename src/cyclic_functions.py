from functools import wraps
from datetime import date
from datetime import datetime as dt
from time import strptime
from telebot import TeleBot
from configparser import ConfigParser

import src.general_functions as gf
import src.auxiliary_functions as af


def planned_execution(period, description):
    """ A decorator that limits the frequency of calls to the decorated function to once for a given period of time.

    Example of the usage:

    @planned_execution('week', [[date(2022, 1, 5)], ['00:00']])
    def new_cyclic_function(bot, user_config, config_path, description, **kwargs):
        pass

    Note:
        user_config, config_path and description parameters must be present in the decored function,
        otherwise the decorator will raise an error. datetime parameter (list[int, str]): [day of period, daytime].
        Day of period: 1-7 for week, 1-31 for month, 1-365 for year. Daytime as 'HH:MM' (for example '23:59').

    Args:
        period (str): 'weekly' or 'month' or 'year'.
        description (str): name of variable in user_config.ini

    """

    def _planned_execution(f):

        @wraps(f)
        def inner(**kwargs):
            user_config = ConfigParser()
            config_path = kwargs['config_path']
            user_id = kwargs['user_id']

            user_config.read(config_path.format(user_id))
            datetimes = user_config['Cyclic'][description]
            datetimes = datetimes.split('/')

            last_usage = user_config['DontChangeIt'][description.replace('_action', '')]

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
                    last_day, _ = last_usage.split(' ')
                    last_day = af.strpdate(last_day, '%d.%m.%Y')

                    if date.today().weekday() == day_of_week and date.today() >= last_day:
                        if time_check(daytime, last_usage, user_id, user_config, description, config_path):
                            f(description=description, **kwargs)

                # monthly cycle
                if period == 'month':
                    day_of_month, daytime = datetime
                    last_day, _ = last_usage.split(' ')
                    last_day = af.strpdate(last_day, '%d.%m.%Y')

                    if date.today().day == day_of_month and date.today() >= last_day:
                        if time_check(daytime, last_usage, user_id, user_config, description, config_path):
                            f(description=description, **kwargs)

        return inner

    return _planned_execution


def time_check(daytime, last_usage: str, user_id, user_config, description, config_path):
    """

    Check last_time < daytime <= time_now
    and change the datetime of last use (last_usage) if the inequality is true .

    Args:
        daytime (str): time as 'HH:MM'.
        last_usage (list[list, list]): last usage of cyclic function. Read planned_execution().
        user_id: user ID.
        user_config (ConfigParser): config.
        description (str): name of variable in user_config.ini
        config_path (str): config path

    Returns:
        (bool): True if the inequality is true. False otherwise.

    """
    last_day, last_time = last_usage.split(' ')  # Date(), str
    last_day = af.strpdate(last_day, '%d.%m.%Y')

    if date.today() == last_day:
        last_time = strptime(last_time, '%H:%M')
    else:
        last_time = strptime('00:00', '%H:%M')

    if last_time < strptime(daytime, '%H:%M') <= \
            strptime(dt.now().strftime('%H:%M'), '%H:%M'):
        last_day = af.dd_mm_yyyy(date.today())
        if strptime(daytime, '%H:%M') > strptime(dt.now().strftime('%H:%M'), '%H:%M'):
            last_time = daytime
        else:
            last_time = dt.now().strftime('%H:%M')

        last_usage = last_day + ' ' + last_time
        user_config['DontChangeIt'][description.replace('_action', '')] = last_usage
        with open(config_path.format(user_id), 'w') as configfile:
            user_config.write(configfile)
        return True
    return False


@planned_execution(period='week', description='weekly_action')
def show_weekly_costs_stats(bot: TeleBot, config_path: str, description: str, user_id):
    """ In each function call all parameters should be entered as kwargs. """
    _ = config_path, description
    bot.send_message(user_id, af.get_phrase(user_id, 40))
    gf.show_costs_stats(bot, user_id, 'weekly_stats')


@planned_execution(period='month', description='monthly_action')
def show_monthly_costs_stats(bot: TeleBot, config_path: str, description: str, user_id):
    """ In each function call all parameters should be entered as kwargs. """
    _ = config_path, description
    bot.send_message(user_id, af.get_phrase(user_id, 41))
    gf.show_costs_stats(bot, user_id, 'monthly_stats')


@planned_execution(period='week', description='weekly_reminder_action')
def send_good_morning(bot: TeleBot, config_path: str, description: str, user_id):
    """ In each function call all parameters should be entered as kwargs. """
    _ = config_path, description
    bot.send_message(user_id, af.get_phrase(user_id, 42))
