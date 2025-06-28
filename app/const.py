import pygame

WIDTH = 960
HEIGHT = 640

USER = "Person:"
PROMPT_TEXT = "GHOST"

STAGE_SCREEN = "menu" 

OPENING_SENTENCE = "Signal the trace. We are listening..."

INIT_POINT_X = 482 - 30
INIT_POINT_Y = 50
MAX_SPEED = 20
TIMEOUT_FACTOR = 2
FPS = 30
VELOCITY = 2
MOVE_MODE = 1 # 1: normal, 2: teleport
ACTIVATE_NODES = 1 # 1: true, 0: false
TRIGGER_MODE = 1 # 1: true, 0: false
HAUNTED_MODE = 0 # 1: true, 0: false

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
  ' ': {"pos": (482-20, 482 + -26), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '?': {"pos": (668-60, 70 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '!': {"pos": (558 + 35, 70 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  # '*': {"pos": (482, 482 + -20), "nodes": []},
  # '&': {"pos": (482, 482 + -20), "nodes": []},

  'A': {"pos": (95  - 8, 234 + -26), "nodes": ["T"], "offset_pos": pygame.Vector2(0, 0)},
  'B': {"pos": (252 - 10, 234 + -26), "nodes": ["U"], "offset_pos": pygame.Vector2(0, 0)},
  'C': {"pos": (405 - 10, 234 + -26), "nodes": ["Z"], "offset_pos": pygame.Vector2(0, 0)},
  'D': {"pos": (558 - 10, 234 + -26), "nodes": ["W"], "offset_pos": pygame.Vector2(0, 0)},
  'E': {"pos": (707 - 8, 234 + -26), "nodes": ["X"], "offset_pos": pygame.Vector2(0, 5)},
  'F': {"pos": (858, 234 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},

  'G': {"pos": (95-8, 289 + -26), "nodes": ["N"], "offset_pos": pygame.Vector2(0, 0)},
  'H': {"pos": (252-12, 289 + -20), "nodes": ["O"], "offset_pos": pygame.Vector2(0, 0)},
  'I': {"pos": (405-8, 289 + -20), "nodes": ["V"], "offset_pos": pygame.Vector2(0, 0)},
  'J': {"pos": (558-8, 289 + -26), "nodes": ["Q"], "offset_pos": pygame.Vector2(0, 0)},
  'K': {"pos": (707-8, 289 + -20), "nodes": ["R"], "offset_pos": pygame.Vector2(0, 0)},
  'L': {"pos": (858, 289 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},

  'M': {"pos": (95-12, 345 + -20), "nodes": ["H"], "offset_pos": pygame.Vector2(0, 0)},
  'N': {"pos": (252-12, 345 + -20), "nodes": ["I"], "offset_pos": pygame.Vector2(0, 0)},
  'O': {"pos": (405-10, 345 + -20), "nodes": ["P"], "offset_pos": pygame.Vector2(0, -11)},
  'P': {"pos": (558-12, 345 + -26), "nodes": ["K"], "offset_pos": pygame.Vector2(0, 8)},
  'Q': {"pos": (707-8, 345 + -20), "nodes": ["L"], "offset_pos": pygame.Vector2(0, 0)},
  'R': {"pos": (858, 345 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},

  'S': {"pos": (95-8, 401 + -20), "nodes": ["B"], "offset_pos": pygame.Vector2(0, 0)},
  'T': {"pos": (252-8, 401 + -16), "nodes": ["C"], "offset_pos": pygame.Vector2(0, 0)},
  'U': {"pos": (405-12, 401 + -20), "nodes": ["J"], "offset_pos": pygame.Vector2(0, 0)},
  'V': {"pos": (558-12, 401 + -20), "nodes": ["E"], "offset_pos": pygame.Vector2(0, 0)},
  'W': {"pos": (707-12, 401 + -20), "nodes": ["F"], "offset_pos": pygame.Vector2(0, -6)},
  'X': {"pos": (858-8, 401 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, -6)},

  'Y': {"pos": (404-12, 463 + -26), "nodes": ["D"], "offset_pos": pygame.Vector2(0, 0)},
  'Z': {"pos": (556-10, 463 + -26), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},

  '0': {"pos": (92, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '1': {"pos": (150, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '2': {"pos": (206, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '3': {"pos": (268, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '4': {"pos": (328, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},

  '5': {"pos": (638, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '6': {"pos": (699, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '7': {"pos": (758, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '8': {"pos": (815, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)},
  '9': {"pos": (875, 464 + -20), "nodes": [], "offset_pos": pygame.Vector2(0, 0)}
}