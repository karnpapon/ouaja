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

# direction: 1=left -> right, -1=left <- right
CHARACTERS = {
  ' ': {"operation": "space", "pos": (462, 456), "right_nodes": [], "node_index": 0,  "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '?': {"pos": (608, 50), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '!': {"pos": (593, 50), "right_nodes": [],"node_index": 0,  "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  # '*': {"pos": (482, 462), "right_nodes": []},
  # '&': {"pos": (482, 462), "right_nodes": []},

  'A': {"pos": (87, 208), "right_nodes": ["T", "H", "N"], "left_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 6), "offset_pos_from": pygame.Vector2(35, 22)},
  'B': {"pos": (242, 208), "right_nodes": ["U", "Y", "I", "O"], "left_nodes": ["S", "G", "M"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 24), "offset_pos_from": pygame.Vector2(35, 22)},
  'C': {"pos": (395, 208), "right_nodes": ["Z", "J", "P", "V"], "left_nodes": ["T", "H", "N"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(15, 10), "offset_pos_from": pygame.Vector2(35, 22)},
  'D': {"operation": "distribute", "pos": (548, 208), "right_nodes": ["W", "K", "Q"], "left_nodes": ["Y", "I", "O", "U"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 24), "offset_pos_from": pygame.Vector2(35, 26)},
  'E': {"pos": (699, 208), "right_nodes": ["X", "L", "R"], "left_nodes": ["V", "Z", "J", "P"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 5), "offset_pos_from": pygame.Vector2(35, 22)},
  'F': {"pos": (858, 214), "right_nodes": [], "left_nodes": ["W", "K", "Q"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(20, 26), "offset_pos_from": pygame.Vector2(35, 22)},

  'G': {"pos": (87, 263), "right_nodes": ["N", "T", "B", "H"], "left_nodes": [], "node_index": 0,"direction": 1, "offset_pos_to": pygame.Vector2(35, 26), "offset_pos_from": pygame.Vector2(35, 26)},
  'H': {"pos": (240, 269), "right_nodes": ["O", "U", "Y", "C", "I"], "left_nodes": ["M", "S", "A", "G"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(24, 20), "offset_pos_from": pygame.Vector2(35, 20)},
  'I': {"pos": (397, 269), "right_nodes": ["V", "Z", "D", "J", "P"], "left_nodes": ["N", "T", "B", "H"],"node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(20, 22), "offset_pos_from": pygame.Vector2(35, 22)},
  'J': {"pos": (550, 263), "right_nodes": ["Q", "W", "E", "K"], "left_nodes": ["U", "Y", "C", "I", "O"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 24), "offset_pos_from": pygame.Vector2(35, 26)},
  'K': {"pos": (699, 269), "right_nodes": ["R", "X", "F", "L"], "left_nodes": ["P", "V", "Z", "D", "J"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(20, 22), "offset_pos_from": pygame.Vector2(35, 16)},
  'L': {"operation": "linger", "pos": (858, 269), "right_nodes": [], "left_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(15, 16), "offset_pos_from": pygame.Vector2(-22, 16)},

  'M': {"pos": (83, 325), "right_nodes": ["H", "N", "T", "B"], "left_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 6), "offset_pos_from": pygame.Vector2(35, 22)},
  'N': {"pos": (240, 325), "right_nodes": ["I", "O", "U", "Y", "C"], "left_nodes": ["G", "M", "S", "A"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(25, 10), "offset_pos_from": pygame.Vector2(35, 22)},
  'O': {"pos": (395, 325), "right_nodes": ["P", "V", "Z", "D", "J"], "left_nodes": ["H", "N", "T", "B"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 0), "offset_pos_from": pygame.Vector2(35, 22)},
  'P': {"pos": (546, 319), "right_nodes": ["K", "Q", "W", "E"], "left_nodes": ["O", "U", "Y", "C", "I"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(28, 10), "offset_pos_from": pygame.Vector2(35, 26)},
  'Q': {"pos": (699, 325), "right_nodes": ["L", "R", "X", "F"], "left_nodes": ["J", "P", "V", "Z", "D"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, -10), "offset_pos_from": pygame.Vector2(35, 22)},
  'R': {"pos": (858, 325), "right_nodes": [], "left_nodes": ["K", "Q", "W","E"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 0), "offset_pos_from": pygame.Vector2(35, 22)},

  'S': {"operation": "shift", "pos": (87, 381), "right_nodes": ["B", "H", "N", "T"], "left_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 24), "offset_pos_from": pygame.Vector2(35, 22)},
  'T': {"pos": (244, 385), "right_nodes": ["C", "I", "O", "U", "Y"], "left_nodes": ["A", "G", "M", "S"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 11), "offset_pos_from": pygame.Vector2(35, 22)},
  'U': {"pos": (393, 381), "right_nodes": ["J", "P", "V", "Z", "D"], "left_nodes": ["B", "H", "N", "T"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 11), "offset_pos_from": pygame.Vector2(35, 22)},
  'V': {"pos": (546, 381), "right_nodes": ["E", "K", "Q", "W"], "left_nodes": ["I", "O", "U", "Y", "C"],"node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 10), "offset_pos_from": pygame.Vector2(35, 22)},
  'W': {"pos": (695, 381), "right_nodes": ["F", "L", "R", "X"], "left_nodes": ["D", "J", "P", "V", "Z"],"node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 6), "offset_pos_from": pygame.Vector2(35, 22)},
  'X': {"pos": (850, 381), "right_nodes": [], "left_nodes": ["E", "K", "Q", "W"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 6), "offset_pos_from": pygame.Vector2(35, 22)},

  'Y': {"pos": (392, 437), "right_nodes": ["D", "J", "P", "V", "Z"],"left_nodes": ["B", "H", "N", "T"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 11), "offset_pos_from": pygame.Vector2(35, 22)},
  'Z': {"pos": (546, 437), "right_nodes": [], "left_nodes": ["C", "I", "O", "U", "Y"], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(35, 11), "offset_pos_from": pygame.Vector2(35, 22)},

  '0': {"pos": (92, 444), "right_nodes": ["E", "K", "Q", "W"], "node_index": 0,  "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '1': {"pos": (150, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '2': {"pos": (206, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '3': {"pos": (268, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '4': {"pos": (328, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},

  '5': {"pos": (638, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '6': {"pos": (699, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '7': {"pos": (758, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '8': {"pos": (815, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)},
  '9': {"pos": (875, 444), "right_nodes": [], "node_index": 0, "direction": 1, "offset_pos_to": pygame.Vector2(0, 0), "offset_pos_from": pygame.Vector2(0, 0)}
}