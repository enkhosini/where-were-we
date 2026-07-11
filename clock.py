"""
clock.py — a tiny local library for working with 24h clock times.

Times can be given as:
    "HH:MM"        e.g. "09:05"
    "HH:MM:SS"     e.g. "09:05:30"
    (h, m)         e.g. (9, 5)
    (h, m, s)      e.g. (9, 5, 30)

Usage:
    from clock import clock, flat, scroll, scroll_iter

    scroll("23:50", "00:10")                     # minute steps, wraps past midnight
    scroll("09:00:00", "09:00:30", interval=5)    # every 5 seconds
    scroll("09:00", "12:00", interval={"hours": 1})
    for t in scroll_iter("00:00", "23:59:59", interval=1):
        ...                                       # stream without building a full list
"""

SECONDS_IN_DAY = 24 * 60 * 60

__all__ = ["clock", "flat", "scroll", "scroll_iter", "next_time", "prev_time"]

# `clock` and `flat` are built lazily on first access (via module __getattr__
# below) rather than at import time, so importing this module costs almost
# nothing unless you actually use the precomputed minute lists.
_clock_cache = None
_flat_cache = None


def _build_clock():
    return [[f"{hour:02d}:{minute:02d}" for minute in range(60)] for hour in range(24)]


def __getattr__(name):
    global _clock_cache, _flat_cache
    if name == "clock":
        if _clock_cache is None:
            _clock_cache = _build_clock()
        return _clock_cache
    if name == "flat":
        if _flat_cache is None:
            _flat_cache = [t for hour_list in (_clock_cache or _build_clock()) for t in hour_list]
        return _flat_cache
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _to_seconds(t):
    """Normalize a time ('HH:MM', 'HH:MM:SS', (h,m) or (h,m,s)) to seconds since midnight."""
    if isinstance(t, str):
        parts = t.split(":")
    elif isinstance(t, (tuple, list)):
        parts = t
    else:
        raise TypeError(f"Unsupported time type: {type(t)!r}")

    n = len(parts)
    if n == 2:
        h, m = int(parts[0]), int(parts[1])
        s = 0
    elif n == 3:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        raise ValueError(f"Invalid time: {t!r}")

    if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
        raise ValueError(f"Invalid time: {t!r}")

    return h * 3600 + m * 60 + s


def _to_str(total_seconds, with_seconds):
    total_seconds %= SECONDS_IN_DAY
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    if with_seconds:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}"


def _interval_to_seconds(interval):
    """
    Normalize an interval to seconds. Accepts:
        int                          -> treated as seconds
        (h, m, s) or (h, m)          -> tuple/list
        {"hours": .., "minutes": .., "seconds": ..}
        "HH:MM:SS" / "HH:MM"         -> string duration
    """
    if isinstance(interval, bool):
        raise TypeError("interval must be numeric, not bool")

    if isinstance(interval, int):
        seconds = interval
    elif isinstance(interval, dict):
        seconds = (
            interval.get("hours", 0) * 3600
            + interval.get("minutes", 0) * 60
            + interval.get("seconds", 0)
        )
    elif isinstance(interval, (tuple, list)):
        n = len(interval)
        if n == 2:
            h, m, s = interval[0], interval[1], 0
        elif n == 3:
            h, m, s = interval
        else:
            raise ValueError(f"Invalid interval: {interval!r}")
        seconds = h * 3600 + m * 60 + s
    elif isinstance(interval, str):
        seconds = _to_seconds(interval)
    else:
        raise TypeError(f"Unsupported interval type: {type(interval)!r}")

    if seconds <= 0:
        raise ValueError("interval must be greater than 0 seconds")

    return seconds


def _scroll_offsets(start, end, interval, inclusive):
    """Shared setup for scroll/scroll_iter. Returns (start_s, with_seconds, range_of_offsets)."""
    start_s = _to_seconds(start)
    end_s = _to_seconds(end)
    step = _interval_to_seconds(interval)

    with_seconds = (step % 60 != 0) or (start_s % 60 != 0) or (end_s % 60 != 0)

    span = end_s - start_s
    if span < 0:
        span += SECONDS_IN_DAY  # wrap around midnight

    upper = span + 1 if inclusive else span
    # range() is O(1) memory regardless of size — no intermediate list is built.
    return start_s, with_seconds, range(0, upper, step)


def scroll(start, end, interval=60, inclusive=True):
    """
    Return the list of times from `start` to `end`, stepping by `interval`
    and wrapping past midnight if end comes before start.

    start, end: 'HH:MM', 'HH:MM:SS', (h, m) or (h, m, s)
    interval:   step size — int seconds, (h, m, s) tuple, {"hours":.., "minutes":.., "seconds":..}
                dict, or 'HH:MM:SS' string duration. Default is 60 (1 minute).
    inclusive:  include the end time in the result (default True)

    Output is formatted as "HH:MM:SS" if the interval or either endpoint
    involves seconds, otherwise "HH:MM".

    For very large ranges (e.g. a full day at 1-second resolution), prefer
    `scroll_iter` to avoid materializing the whole list in memory.
    """
    start_s, with_seconds, offsets = _scroll_offsets(start, end, interval, inclusive)
    return [_to_str(start_s + off, with_seconds) for off in offsets]


def scroll_iter(start, end, interval=60, inclusive=True):
    """
    Same as `scroll`, but returns a generator instead of a list — O(1) memory
    no matter how large the range is. Use this when streaming/consuming times
    one at a time (e.g. `for t in scroll_iter(...): ...`).
    """
    start_s, with_seconds, offsets = _scroll_offsets(start, end, interval, inclusive)
    for off in offsets:
        yield _to_str(start_s + off, with_seconds)


def next_time(t, interval=60):
    """Return the time `interval` after `t` (default 1 minute), wrapping past midnight."""
    t_s = _to_seconds(t)
    step = _interval_to_seconds(interval)
    with_seconds = (step % 60 != 0) or (t_s % 60 != 0)
    return _to_str(t_s + step, with_seconds)


def prev_time(t, interval=60):
    """Return the time `interval` before `t` (default 1 minute), wrapping before midnight."""
    t_s = _to_seconds(t)
    step = _interval_to_seconds(interval)
    with_seconds = (step % 60 != 0) or (t_s % 60 != 0)
    return _to_str(t_s - step, with_seconds)


if __name__ == "__main__":
    # quick demo
    print(scroll("23:57", "00:03"))
    print(scroll("09:00:00", "09:00:30", interval=5))
    print(list(scroll_iter("00:00", "12:00", interval={"hours": 3})))
    print(next_time("23:59:50", interval=15))