# -*- coding: utf-8 -*-


from __future__ import absolute_import

import datetime as abs_datetime
from pyframework.util.datetime.timezone import TimezoneHelper
from pyframework.util.datetime import DatetimeHelper


class DateHelper:
    @staticmethod
    def now( timezone=None):
        return DateHelper.from_datetime(datetime=DatetimeHelper.now(timezone=timezone))

    @staticmethod
    def from_datetime( datetime, timezone=None):
        if not timezone:
            return abs_datetime.datetime(
                year=datetime.year,
                month=datetime.month,
                day=datetime.day,
                tzinfo=datetime.tzinfo)

        if not datetime.tzinfo:
            datetime = TimezoneHelper.localize(datetime=datetime, timezone=timezone)
        else:
            datetime = TimezoneHelper.normalize(datetime=datetime, timezone=timezone)

        return DateHelper.from_datetime(datetime=datetime)

    @staticmethod
    def from_timestamp( timestamp, timezone=None, ms=False):
        datetime = DatetimeHelper.from_timestamp(timestamp=timestamp, timezone=timezone, ms=ms)
        return DateHelper.from_datetime(datetime=datetime)

    @staticmethod
    def convert(
            
            auto=None,
            datetime=None,
            timezone=None,
            timestamp=None,
            yyyymmdd=None,
            yyyymmddhhiiss=None,
            ms=False):
        datetime = DatetimeHelper.convert(
            auto=auto,
            datetime=datetime,
            timezone=timezone,
            timestamp=timestamp,
            yyyymmdd=yyyymmdd,
            yyyymmddhhiiss=yyyymmddhhiiss,
            ms=ms)
        return DateHelper.from_datetime(datetime=datetime)

    @staticmethod
    def year( auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).year

    @staticmethod
    def month( auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).month

    @staticmethod
    def day( auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).day

    @staticmethod
    def weekday( auto=None, datetime=None, timezone=None, timestamp=None, ms=False, isoweekday=True):
        datetime = DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        return datetime.isoweekday() if isoweekday else datetime.weekday()

    @staticmethod
    def tuple( auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        datetime = DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        time_set = [datetime.year, datetime.month, datetime.day]

        if datetime.tzinfo:
            time_set.append(TimezoneHelper.zone_from_tzinfo(datetime.tzinfo))

        return time_set

    @staticmethod
    def yyyymmdd( auto=None, datetime=None, timezone=None, timestamp=None, ms=False, concat=''):
        datetime = DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        return '%04d%s%02d%s%02d' % (datetime.year, concat, datetime.month, concat, datetime.day)

    @staticmethod
    def mmdd( auto=None, datetime=None, timezone=None, timestamp=None, ms=False, concat=''):
        datetime = DateHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        return '%02d%s%02d' % (datetime.month, concat, datetime.day)
