# src/datagen/utils.py
import random
from datetime import date, timedelta


def set_seed(seed: int | None):
    """
    Set random seed for reproducibility.
    """
    if seed is not None:
        random.seed(seed)


def random_date(start_year=1970, end_year=2005):
    """
    Generate a random date between two years.
    """
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))
