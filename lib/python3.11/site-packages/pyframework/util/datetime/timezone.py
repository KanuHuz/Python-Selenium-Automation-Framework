# -*- coding: utf-8 -*-


from pytz import timezone as pytz_timezone
from pyframework.util.type.check import ObjectCheckHelper

class TimezoneHelper:
    @staticmethod
    def tzinfo_from_zone( zone):
        return pytz_timezone(zone)

    @staticmethod
    def zone_from_tzinfo( zone):
        if not zone or not hasattr(zone, 'zone'):
            return None

        return zone.zone

    @staticmethod
    def tzinfo_from_datetime( datetime):
        return datetime.tzinfo

    @staticmethod
    def zone_from_datetime( datetime):
        return TimezoneHelper.zone_from_tzinfo(datetime.tzinfo)

    @staticmethod
    def localize( datetime, timezone):
        return timezone.localize(datetime)

    @staticmethod
    def normalize( datetime, timezone):
        if ObjectCheckHelper.string(timezone):
            timezone = TimezoneHelper.tzinfo_from_zone(timezone)

        return timezone.normalize(datetime)
