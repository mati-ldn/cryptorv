import pandas as pd
from datetime import datetime, timedelta


def get_expiries():
    """
    Returns the dates of the last Fridays of March, June, September, and December of the next year if needed.
    """
    today = datetime.today()
    current_year = today.year
    target_months = [3, 6, 9, 12]  # March, June, September, December

    def last_friday_of_month(year, month):
        """Returns the date of the last Friday of the given month and year."""
        # Get the last day of the month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day_of_month = next_month - timedelta(days=1)

        # Find the last Friday
        offset = (last_day_of_month.weekday() - 4) % 7
        last_friday = last_day_of_month - timedelta(days=offset)
        return last_friday

    result_dates = []
    for month in target_months:
        if today.month > month or (
            today.month == month
            and today.day > last_friday_of_month(current_year, month).day
        ):
            # If we are past the target month, move to next year
            result_dates.append(last_friday_of_month(current_year + 1, month))
        else:
            result_dates.append(last_friday_of_month(current_year, month))

    return result_dates


if __name__ == '__main__':
    dates = get_expiries()
    print(dates)
