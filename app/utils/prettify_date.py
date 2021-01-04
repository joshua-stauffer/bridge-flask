month_map = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
st_suffix = {1, 21, 31}
nd_suffix = {2, 22}
rd_suffix = {3, 23}

def prettify_date(date):
    if not date: return ''
    month = month_map[date.month]
    if date.day in st_suffix:
        day = str(date.day) + 'st'
    elif date.day in nd_suffix:
        day = str(date.day) + 'nd'
    elif date.day in rd_suffix:
        day = str(date.day) + 'rd'
    else:
        day = str(date.day) + 'th'
    
    return f'{month} {day}, {date.year}'