from datetime import date

# Idea to find the number of weeks in a year
# https://stackoverflow.com/questions/29262859/the-number-of-calendar-weeks-in-a-year
def number_of_weeks(year):
    last_week = date(year, 12, 28)
    return last_week.isocalendar().week