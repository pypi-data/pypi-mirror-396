# profiles.py
from .config import FIRST_NAMES, LAST_NAMES
import random

def generate_profiles(n=10):
    profiles = []
    for _ in range(n):
        profiles.append({
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "age": random.randint(18, 70)
        })
    return profiles
