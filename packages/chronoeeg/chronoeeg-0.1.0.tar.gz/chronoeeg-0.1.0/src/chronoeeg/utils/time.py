"""Time handling utilities."""

from datetime import datetime, time, timedelta
from typing import Tuple


class TimeHelper:
    """Helper class for time-related operations."""

    @staticmethod
    def parse_time_string(time_str: str) -> time:
        """
        Parse time string in HH:MM:SS format.

        Parameters
        ----------
        time_str : str
            Time string to parse

        Returns
        -------
        time
            Parsed time object
        """
        hours, minutes, seconds = (int(x) for x in time_str.split(":"))
        return time(hours, minutes, seconds)

    @staticmethod
    def time_diff_seconds(start: time, end: time) -> float:
        """
        Calculate difference between two times in seconds.

        Parameters
        ----------
        start : time
            Start time
        end : time
            End time

        Returns
        -------
        float
            Difference in seconds
        """
        start_dt = datetime.combine(datetime.today(), start)
        end_dt = datetime.combine(datetime.today(), end)
        return (end_dt - start_dt).total_seconds()

    @staticmethod
    def add_seconds_to_time(t: time, seconds: float) -> time:
        """
        Add seconds to a time object.

        Parameters
        ----------
        t : time
            Base time
        seconds : float
            Seconds to add

        Returns
        -------
        time
            New time
        """
        dt = datetime.combine(datetime.today(), t)
        dt += timedelta(seconds=seconds)
        return dt.time()
