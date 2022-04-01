import random

chars = {
    'all': [chr(i) for i in range(33, 127)],
    'numbers': [chr(i) for i in range(48, 58)],
    'letters': [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)],
    'upper_case': [chr(i) for i in range(65, 91)],
    'lower_case': [chr(i) for i in range(97, 123)],
    'punctuation': [chr(i) for i in range(33, 48)] + [chr(i) for i in range(58, 65)] + [chr(i) for i in range(91, 97)] + [chr(i) for i in range(123, 127)]
}


def random_string(length=16):
    return ''.join(random.choice(chars['all']) for i in range(length))


def random_letters(length=20):
    return ''.join(random.choice(chars['letters']) for i in range(length))
