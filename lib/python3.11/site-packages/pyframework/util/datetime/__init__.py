# -*- coding: utf-8 -*-


from __future__ import absolute_import

import time
import datetime as abs_datetime
from pyframework.util.datetime.timezone import TimezoneHelper
from pyframework.util.type.check import ObjectCheckHelper
from pyframework.util.numeric.cast import CastHelper
from pyframework.util.numeric import NumericHelper


class DatetimeHelper:
    @staticmethod
    def now(timezone=None):
        return abs_datetime.datetime.now(tz=timezone)

    @staticmethod
    def from_datetime(datetime, timezone=None):
        if not timezone:
            return datetime

        if not datetime.tzinfo:
            return TimezoneHelper.localize(datetime=datetime, timezone=timezone)
        else:
            return TimezoneHelper.normalize(datetime=datetime, timezone=timezone)

    @staticmethod
    def from_timestamp(timestamp, timezone=None, ms=False):
        timestamp = CastHelper.long(timestamp)

        # TZ Info from Zone
        if timezone and ObjectCheckHelper.string(timezone):
            timezone = TimezoneHelper.tzinfo_from_zone(timezone)

        if ms:  # with microseconds
            datetime = abs_datetime.datetime.fromtimestamp(timestamp // 1000, tz=timezone)
            datetime = datetime.replace(microsecond=timestamp % 1000 * 1000)
            return datetime
        else:
            return abs_datetime.datetime.fromtimestamp(timestamp, tz=timezone)

    @staticmethod
    def transform(anonymous):
        if isinstance(anonymous, abs_datetime.datetime):
            return {'datetime': anonymous}

        if ObjectCheckHelper.string(anonymous):
            anonymous_cast = NumericHelper.extract_numbers(anonymous)

            if len(anonymous_cast) != len(anonymous):
                raise Exception('The specified value is invalid.')

            if len(anonymous) == 8:  # yyyymmdd
                return {'yyyymmdd': anonymous}
            elif len(anonymous) == 14:  # yyyymmddhhiiss
                return {'yyyymmddhhiiss': anonymous}
            else:
                raise Exception('The specified value is invalid.')

        elif ObjectCheckHelper.numeric(anonymous):
            if anonymous < 10000000000:  # timestamp
                return {'timestamp': CastHelper.int(anonymous)}
            else:  # timestamp with ms
                return {'timestamp': CastHelper.long(anonymous), 'ms': True}

        else:
            raise Exception('The specified value is invalid.')

    @staticmethod
    def convert(
            auto=None,
            datetime=None,
            timezone=None,
            timestamp=None,
            yyyymmdd=None,
            yyyymmddhhiiss=None,
            ms=False):
        if auto:
            return DatetimeHelper.convert(**DatetimeHelper.transform(auto))

        if isinstance(datetime, abs_datetime.datetime):
            if timezone:
                datetime = DatetimeHelper.from_datetime(datetime=datetime, timezone=timezone)
        elif timestamp:
            if ObjectCheckHelper.numeric(timestamp):
                datetime = DatetimeHelper.from_timestamp(timestamp=timestamp, timezone=timezone, ms=ms)
            else:
                raise Exception('The specified timestamp value is invalid.')
        elif yyyymmdd:
            if len(NumericHelper.extract_numbers(str(yyyymmdd))) == 8:
                timestamp = DatetimeHelper.helper.datetime.timestamp.mktime(
                    year=int(yyyymmdd[0:4]),
                    month=int(yyyymmdd[4:6]),
                    day=int(yyyymmdd[6:8]),
                    ms=ms)

                return DatetimeHelper.convert(timestamp=timestamp, timezone=timezone, ms=ms)
            else:
                raise Exception('The spcified yyyymmdd value is invalid.')
        elif yyyymmddhhiiss:
            if len(NumericHelper.extract_numbers(str(yyyymmddhhiiss))) == 14:
                timestamp = DatetimeHelper.helper.datetime.timestamp.mktime(
                    year=int(yyyymmddhhiiss[0:4]),
                    month=int(yyyymmddhhiiss[4:6]),
                    day=int(yyyymmddhhiiss[6:8]),
                    hour=int(yyyymmddhhiiss[8:10]),
                    minute=int(yyyymmddhhiiss[10:12]),
                    second=int(yyyymmddhhiiss[12:14]),
                    ms=ms)

                return DatetimeHelper.convert(timestamp=timestamp, timezone=timezone, ms=ms)
            else:
                raise Exception('The spcified yyyymmdd value is invalid.')
        elif not datetime:
            datetime = DatetimeHelper.now(timezone=timezone)
        else:
            raise Exception('The specified datetime value is invalid.')

        return datetime

    @staticmethod
    def tuple(auto=None, datetime=None, timezone=None, timestamp=None, ms=False):
        datetime = DatetimeHelper.convert(auto=auto, datetime=datetime, timezone=timezone, timestamp=timestamp, ms=ms)
        time_set = [datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute, datetime.second]

        if ms:
            time_set.append(datetime.microsecond)

        if datetime.tzinfo:
            time_set.append(TimezoneHelper.zone_from_tzinfo(datetime.tzinfo))

        return time_set
