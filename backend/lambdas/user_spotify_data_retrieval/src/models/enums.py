from enum import Enum


class TimeRange(str, Enum):
    SHORT_TERM = "short_term"  # approx last 4 weeks
    MEDIUM_TERM = "medium_term"  # approx last 6 months
    LONG_TERM = "long_term"  # approx last 12 months
