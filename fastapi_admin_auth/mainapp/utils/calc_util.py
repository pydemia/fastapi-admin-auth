import datetime as dt

__all__ = [
    "calc_elapsed_time",
]


def calc_elapsed_time(x, y):
    
    if x is None or y is None:
        return None

    dt_x = x.replace(tzinfo=None)
    dt_y = y.replace(tzinfo=None)
    return str(dt_x - dt_y) if x >= y else str(dt_y - dt_x)