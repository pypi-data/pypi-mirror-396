from .config import REGIONS
import random

def generate_regions(n=5):
    return [random.choice(REGIONS) for _ in range(n)]
