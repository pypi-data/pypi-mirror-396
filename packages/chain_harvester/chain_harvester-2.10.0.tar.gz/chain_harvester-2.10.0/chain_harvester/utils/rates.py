from decimal import Decimal

from chain_harvester.constants import SECONDS_PER_YEAR


def calculate_average_rate(previous_index, previous_time, current_index, current_time):
    if previous_index <= 0:
        return Decimal("0")

    time_difference = current_time - previous_time
    seconds = Decimal(time_difference.total_seconds())
    if seconds == Decimal(0):
        return Decimal("0")

    period = SECONDS_PER_YEAR / seconds
    return (Decimal(str(current_index)) / Decimal(str(previous_index))) ** period - Decimal("1")


def apr_to_apy(value, periods=SECONDS_PER_YEAR):
    if value is None:
        return None
    return pow((1 + Decimal(value) / Decimal(periods)), Decimal(periods)) - 1


def apy_to_apr(value, periods=SECONDS_PER_YEAR):
    if value is None:
        return None
    periods = Decimal(periods)
    value = Decimal(value)
    return periods * (pow((1 + value), 1 / periods) - 1)
