# -*- coding: utf-8 -*-


from __future__ import absolute_import
from pyframework.util.numeric.cast import  CastHelper
from pyframework.util.datetime import DatetimeHelper
import time as abs_time


class TimestampHelper:
    @staticmethod
    def now(  ms=False):
        return CastHelper.long(abs_time.time() if not ms else round(abs_time.time() * 1000))

    @staticmethod
    def yesterday(
            auto=None,
            timestamp=None,
            datetime=None,
            timezone=None,
            yyyymmdd=None,
            yyyymmddhhiiss=None,
            ms=False):
        timestamp = TimestampHelper.convert(
            auto=auto,
            timestamp=timestamp,
            datetime=datetime,
            timezone=timezone,
            yyyymmdd=yyyymmdd,
            yyyymmddhhiiss=yyyymmddhhiiss,
            ms=ms)

        return timestamp - (3600*24*(1 if not ms else 1000))

    @staticmethod
    def tommorow(
            auto=None,
            timestamp=None,
            datetime=None,
            timezone=None,
            yyyymmdd=None,
            yyyymmddhhiiss=None,
            ms=False):
        timestamp = TimestampHelper.convert(
            auto=auto,
            timestamp=timestamp,
            datetime=datetime,
            timezone=timezone,
            yyyymmdd=yyyymmdd,
            yyyymmddhhiiss=yyyymmddhhiiss,
            ms=ms)

        return timestamp + (3600*24*(1 if not ms else 1000))

    @staticmethod
    def to_datetime(  *args, **kwargs):
        return DatetimeHelper.from_timestamp(*args, **kwargs)

    @staticmethod
    def mktime(  year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, ms=False):
        p_tuple = (
            year,
            month,
            day,
            hour,
            minute,
            second,
            0,
            0,
            0
        )

        timestamp = CastHelper.long(abs_time.mktime(p_tuple))

        if not ms:
            return timestamp
        else:
            return (timestamp * 1000) + microsecond

    @staticmethod
    def from_datetime(  datetime, ms=False):
        return TimestampHelper.mktime(
            year=datetime.year,
            month=datetime.month,
            day=datetime.day,
            hour=datetime.hour,
            minute=datetime.minute,
            second=datetime.second,
            microsecond=datetime.microsecond // 1000,
            ms=ms)

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

        return TimestampHelper.from_datetime(datetime=datetime, ms=ms)
