# -*- coding: utf-8 -*-


from __future__ import absolute_import
from pyframework.util.datetime.timezone import TimezoneHelper
from pyframework.util.datetime import DatetimeHelper


class TimeHelper:
    @staticmethod
    def hour(auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).hour

    @staticmethod
    def minute(auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).minute

    @staticmethod
    def second(auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        return TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms).second

    @staticmethod
    def tuple(auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        datetime = TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        time_set = [datetime.hour, datetime.minute, datetime.second]

        if ms:
            time_set.append(datetime.microsecond)

        if datetime.tzinfo:
            time_set.append(TimezoneHelper.zone_from_tzinfo(datetime.tzinfo))

        return time_set

    @staticmethod
    def hhiiss(auto=None, datetime=None, timezone=None, timestamp=None, ms=False, concat=''):
        datetime = TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        return '%02d%s%02d%s%02d' % (datetime.hour, concat, datetime.minute, concat, datetime.second)

    @staticmethod
    def hhii(auto=None, datetime=None, timezone=None, timestamp=None, ms=False, concat=''):
        datetime = TimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        return '%02d%s%02d' % (datetime.hour, concat, datetime.minute)

    @staticmethod
    def convert(
            auto=None,
            datetime=None,
            timezone=None,
            timestamp=None,
            yyyymmdd=None,
            yyyymmddhhiiss=None,
            ms=False):
        return DatetimeHelper.convert(
            auto=auto,
            datetime=datetime,
            timezone=timezone,
            timestamp=timestamp,
            yyyymmdd=yyyymmdd,
            yyyymmddhhiiss=yyyymmddhhiiss,
            ms=ms)
