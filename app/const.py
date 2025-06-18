WIDTH = 960
HEIGHT = 540

USER = "Person:"
PROMPT_TEXT = "GHOST"

STAGE_SCREEN = "menu" 

OPENING_SENTENCE = "Signal the trace. We are listening..."

INIT_POINT_X = 482 - 53
INIT_POINT_Y = 50
MAX_SPEED = 20
TIMEOUT_FACTOR = 2
FPS = 30
VELOCITY = 2
MOVE_MODE = 1 # 1: normal, 2: teleport
ACTIVATE_NODES = 1 # 1: true, 0: false

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (142, 68, 173)

BG_COLOR = (0, 0, 0)  # B0AEA7
TEXT_COLOR = (255, 0, 0)  # 312F28
TEXT_LIGHTEST_COLOR = (255, 255, 255)  # 7D7866

# Glow data
GLOW_DURATION_FRAMES = 60
GLOW_MAX_ALPHA = 200
GLOW_DURATION = 1  # seconds to fade out

CHARACTERS = {
  ' ': {"pos": (482-20, 482 + -26), "nodes": []},
  '?': {"pos": (668-60, 70 + -20), "nodes": []},
  '!': {"pos": (558 + 35, 70 + -20), "nodes": []},
  # '*': {"pos": (482, 482 + -20), "nodes": []},
  # '&': {"pos": (482, 482 + -20), "nodes": []},

  'A': {"pos": (95  - 8, 234 + -26), "nodes": ["T"]},
  'B': {"pos": (252 - 10, 234 + -26), "nodes": ["U"]},
  'C': {"pos": (405 - 10, 234 + -26), "nodes": ["Z"]},
  'D': {"pos": (558 - 10, 234 + -26), "nodes": ["W"]},
  'E': {"pos": (707 - 8, 234 + -26), "nodes": ["X"]},
  'F': {"pos": (858, 234 + -20), "nodes": []},

  'G': {"pos": (95-8, 289 + -26), "nodes": ["N"]},
  'H': {"pos": (252-12, 289 + -20), "nodes": ["O"]},
  'I': {"pos": (405-8, 289 + -20), "nodes": ["V"]},
  'J': {"pos": (558-8, 289 + -26), "nodes": ["Q"]},
  'K': {"pos": (707-8, 289 + -20), "nodes": ["R"]},
  'L': {"pos": (858, 289 + -20), "nodes": []},

  'M': {"pos": (95-12, 345 + -20), "nodes": ["H"]},
  'N': {"pos": (252-12, 345 + -20), "nodes": ["I"]},
  'O': {"pos": (405-10, 345 + -20), "nodes": ["P"]},
  'P': {"pos": (558-12, 345 + -26), "nodes": ["K"]},
  'Q': {"pos": (707-8, 345 + -20), "nodes": ["L"]},
  'R': {"pos": (858, 345 + -20), "nodes": []},

  'S': {"pos": (95-8, 401 + -20), "nodes": ["B"]},
  'T': {"pos": (252-8, 401 + -16), "nodes": ["C"]},
  'U': {"pos": (405-12, 401 + -20), "nodes": ["J"]},
  'V': {"pos": (558-12, 401 + -20), "nodes": ["E"]},
  'W': {"pos": (707-12, 401 + -20), "nodes": ["F"]},
  'X': {"pos": (858-8, 401 + -20), "nodes": []},

  'Y': {"pos": (404-12, 463 + -26), "nodes": ["D"]},
  'Z': {"pos": (556-10, 463 + -26), "nodes": []},

  '0': {"pos": (92, 464 + -20), "nodes": []},
  '1': {"pos": (150, 464 + -20), "nodes": []},
  '2': {"pos": (206, 464 + -20), "nodes": []},
  '3': {"pos": (268, 464 + -20), "nodes": []},
  '4': {"pos": (328, 464 + -20), "nodes": []},

  '5': {"pos": (638, 464 + -20), "nodes": []},
  '6': {"pos": (699, 464 + -20), "nodes": []},
  '7': {"pos": (758, 464 + -20), "nodes": []},
  '8': {"pos": (815, 464 + -20), "nodes": []},
  '9': {"pos": (875, 464 + -20), "nodes": []}
}