import random


def hello() -> str:
    random_number = random.randint(0, 100)
    return f"Hello {random_number}  from pariadi-test-lib!"
