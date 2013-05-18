"""
sentry.tsdb.utils
~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from datetime import timedelta

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24
ONE_WEEK = ONE_DAY * 7


class Granularity(object):
    SECONDS = 0
    MINUTES = 1
    HOURS = 2
    DAYS = 3
    WEEKS = 4
    MONTHS = 5
    YEARS = 6
    ALL_TIME = 7

    @classmethod
    def get_choices(cls):
        if hasattr(cls, '__choice_cache'):
            return cls.__choice_cache

        results = []
        for name in dir(cls):
            if name.startswith('_'):
                continue
            if not name.upper() == name:
                continue
            results.append((getattr(cls, name), name.replace('_', ' ').title()))
        cls.__choice_cache = results
        return results

    @classmethod
    def normalize_to_epoch(cls, granularity, timestamp):
        """
        Given a ``timestamp`` (datetime object) normalize the datetime object
        ``timestamp`` to an epoch timestmap (integer).

        i.e. if the granularity is minutes, the resulting timestamp would have
        the seconds and microseconds rounded down.
        """
        timestamp = timestamp.replace(microsecond=0)
        if granularity == cls.ALL_TIME:
            return 0
        if granularity == cls.SECONDS:
            return timestamp
        timestamp = timestamp.replace(seconds=0)
        if granularity == cls.MINUTES:
            return timestamp
        timestamp = timestamp.replace(minutes=0)
        if granularity == cls.HOURS:
            return timestamp
        timestamp = timestamp.replace(hours=0)
        if granularity == cls.WEEKS:
            timestamp -= timedelta(days=timestamp.weekday())
        elif granularity in (cls.MONTHS, cls.YEARS):
            timestamp = timestamp.replace(day=1)
        elif granularity == cls.YEARS:
            timestamp = timestamp.replace(month=1)
        return int(timestamp.strftime('%s'))

    @classmethod
    def get_min_timestamp(cls, granularity, timestamp):
        """
        Return the minimum value (as an epoch timestamp) to keep in storage for
        a granularity.

        Timestamp should represent the current time.

        i.e. if the granularity is seconds, the timestamp will be normalized to
        the previous minute so only latest 60 points are stored (one per second)
        """
        if granularity in (cls.ALL_TIME, cls.YEARS):
            return None

        if granularity == cls.SECONDS:
            timestamp -= timedelta(minutes=1)
        elif granularity == cls.MINUTES:
            timestamp -= timedelta(hours=1)
        elif granularity == cls.HOURS:
            timestamp -= timedelta(days=1)
        elif granularity == cls.DAYS:
            # days are stored for a full month
            timestamp -= timedelta(months=1)
        elif granularity == cls.WEEKS:
            # weeks are stored for a full year
            timestamp -= timedelta(years=1)

        return cls.normalize_to_epoch(timestamp, granularity)
