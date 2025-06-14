WIDTH = 960
HEIGHT = 540

USER = "Person:"
PROMPT_TEXT = "GHOST"

INIT_POINT_X = 482
INIT_POINT_Y = 50
MAX_SPEED = 20
TIMEOUT_FACTOR = 2
FPS = 30
VELOCITY = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)

CHARACTERS = {
    ' ': (482-20, 482 + -26),
    '?': (668-60, 70 + -20),
    '!': (558 + 35, 70 + -20),
    # '*': (482, 482 + -20),
    # '&': (482, 482 + -20),

    'A': (95  - 8, 234 + -26),
    'B': (252 - 10, 234 + -26),
    'C': (405 - 10, 234 + -26),
    'D': (558 - 10, 234 + -26),
    'E': (707 - 8, 234 + -26),
    'F': (858, 234 + -20),

    'G': (95-8, 289 + -26),
    'H': (252-12, 289 + -20),
    'I': (405-8, 289 + -20),
    'J': (558-8, 289 + -26),
    'K': (707-8, 289 + -20),
    'L': (858, 289 + -20),

    'M': (95-12, 345 + -20),
    'N': (252-12, 345 + -20),
    'O': (405-10, 345 + -20),
    'P': (558-12, 345 + -26),
    'Q': (707-8, 345 + -20),
    'R': (858, 345 + -20),

    'S': (95-8, 401 + -20),
    'T': (252-8, 401 + -16),
    'U': (405-12, 401 + -20),
    'V': (558-12, 401 + -20),
    'W': (707-12, 401 + -20),
    'X': (858-8, 401 + -20),

    'Y': (404-12, 463 + -26),
    'Z': (556-10, 463 + -26),

    '0': (92, 464 + -20),
    '1': (150, 464 + -20),
    '2': (206, 464 + -20),
    '3': (268, 464 + -20),
    '4': (328, 464 + -20),

    '5': (638, 464 + -20),
    '6': (699, 464 + -20),
    '7': (758, 464 + -20),
    '8': (815, 464 + -20),
    '9': (875, 464 + -20)
}