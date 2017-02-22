from __future__ import print_function
import re
import datetime

def process_numbers(numberList):
    # split on commas
    result = []
    if isinstance(numberList, str):
        numberList = list( num.strip(',') for num in numberList.split() )
    if isinstance(numberList, int):
        numberList = [str(numberList)]
    for item in numberList:
        # if there is a dash then it is a range
        if "-" in item:
            item = [int(i) for i in item.split("-")]
            item.sort()
            if item[0] is not None:
                    result.extend(range(item[0], item[1]+1))
        else:
            result.extend([int(item)])

    result.sort()
    return result

class FixedOffset(datetime.tzinfo):
    """
    Fixed offset in minutes east from UTC. Taken from Python's docs.
    Kept as close as possible to the reference version. __init__ was changed
    to make its arguments optional, according to Python's requirement that
    tzinfo subclasses can be instantiated without arguments.
    """

    def __init__(self, offset=None, name=None):
        if offset is not None:
            self.__offset = datetime.timedelta(minutes=offset)
        if name is not None:
            self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return timedelta(0) 

def get_fixed_timezone(offset):
    """Return a tzinfo instance with a fixed offset from UTC."""
    if isinstance(offset, datetime.timedelta):
        offset = offset.seconds // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    name = sign + hhmm
    return FixedOffset(offset, name)

def parse_datetime(value):
    # from django.utils import  dateparse
    """Parse a string and return a datetime.datetime.
    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.
    Raise ValueError if the input is well formatted but not a valid datetime.
    Return None if the input isn't well formatted.
    """
    datetime_re = re.compile(
        r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
        r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
        r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
        r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
    )

    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = get_fixed_timezone(offset)
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        kw['tzinfo'] = tzinfo
    return datetime.datetime(**kw)

def error(message):
    print()
    print("#---------------------------------------------------------------------#")
    print("# ERROR:", message)
    print("#---------------------------------------------------------------------#")
    print()
    sys.exit()
