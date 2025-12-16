from .config import MIN_SALARY, MAX_SALARY
import random

def generate_salaries(n=10):
    return [random.randint(MIN_SALARY, MAX_SALARY) for _ in range(n)]
