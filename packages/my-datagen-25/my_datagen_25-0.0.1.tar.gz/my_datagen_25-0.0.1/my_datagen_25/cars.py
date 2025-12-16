from .config import CAR_BRANDS
import random

def generate_cars(n=10):
    return [{"brand": random.choice(CAR_BRANDS)} for _ in range(n)]
