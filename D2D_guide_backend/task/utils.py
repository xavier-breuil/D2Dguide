from datetime import date, timedelta
import calendar

# Idea to find the number of weeks in a year
# https://stackoverflow.com/questions/29262859/the-number-of-calendar-weeks-in-a-year
def number_of_weeks(year):
    last_week = date(year, 12, 28)
    return last_week.isocalendar().week

def is_included(sublist, main_list):
    """
    Check if unordered sublist is included in unordered main_list.
    """
    return set(sublist).issubset(set(main_list))

def every_month_clean(start_date, end_date, day_list):
    """
    Make sur that days list can be included in start and end date range.
    Note that this function doesn't check that start_date is before end_date.
    """
    # Get all month ranges
    running_date = start_date
    current_month_range = month_range(running_date.year, running_date.month)
    month_ranges = [current_month_range]
    while (running_date + timedelta(days=current_month_range) < end_date):
        running_date = running_date + timedelta(days=current_month_range)
        month_ranges.append(current_month_range)
        current_month_range = month_range(running_date.year, running_date.month)
    # Make sure that days are positive integers in reasonnable range
    # and that there is no requirement to create a date such as 30th of february
    return (
        max(day_list) <= min(month_ranges) and
        is_included(day_list, [*range(1,32)]))

def remove_duplicate_from_list(data_list):
    """
    remove duplicate from list.
    """
    return list(set(data_list))

def check_dict_list_date_format(dict_list, start_date, end_date):
    """
    Make sur that all elements of the list are dictionnaries with specific keys.
    """
    running_year = start_date.year
    while running_year <= end_date.year:
        for dictionnary in dict_list:
            try:
                date(year=running_year, month=dictionnary['month'], day=dictionnary['day'])
                assert(len(dictionnary) == 2)
            # ValueError for 30/02/2024
            # KeyError for dictionnary['month'] not existing
            # AssertionError for dictionnary = {month: 3, day: 23, other: whatever}
            except(ValueError, KeyError, AssertionError):
                return False
        running_year = running_year + 1
    return True

def month_range(year, month):
    """
    Return the number of days in a month.
    """
    return calendar.monthrange(year, month)[1]