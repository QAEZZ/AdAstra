from random import choice
from string import ascii_letters


def gen(length: int = 7) -> str:
    return "".join(choice(ascii_letters) for x in range(length))
