import re
from . import transitions
from . import states
from . import arg
from . import const
from . import utils
from . import pyganim
from easing_functions import *
from pygame.locals import *
import numpy as np
import queue
import pygame
import pygame_textinput
# from pygame_render import RenderEngine
import sys
import os
import random
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

bg_color = (0, 0, 0)  # B0AEA7
text_color = (255, 0, 0)  # 312F28
text_lightest_color = (255, 255, 255)  # 7D7866

pygame.init()
screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

# engine = RenderEngine(const.WIDTH, const.HEIGHT)
# shader_glow = engine.load_shader_from_path('assets/shaders/vertex.glsl', 'assets/shaders/default.glsl')

def get_center_position(surface: pygame.Surface, screen_size: tuple[int]):
  surface_rect = surface.get_rect()
  return (
      (surface_rect.width - screen_size[0]) // 2,
      (surface_rect.height - screen_size[1]) // 2
  )


# Load soul animation frames dynamically
soul_frame_paths = [
    f"assets/sprites/soul/soul_{i}.png" for i in range(1, 9)
]
soul_frames = [pygame.image.load(path).convert_alpha()
               for path in soul_frame_paths]

spriteAnim = pyganim.PygAnimation([(frame, 0.1) for frame in soul_frames])
spriteAnim.scale((soul_frames[0].get_width() * 5,
                 soul_frames[0].get_height() * 5))
spriteAnim.play()


# Load swirl effect frames dynamically and apply color replacement
swirl_fx_frame_paths = [
    f"assets/sprites/swirl/frame_{i:02d}.png" for i in range(17)
]
swirl_fx_frames = [pygame.image.load(
    path).convert_alpha() for path in swirl_fx_frame_paths]

replace_color_swirl_fx_frames = [
    utils.replace_color(frame, text_color, text_lightest_color, tolerance=0)
    for frame in swirl_fx_frames
]

fx_swirl = pyganim.PygAnimation(
    [(frame, 0.1) for frame in replace_color_swirl_fx_frames],
    loop=False
)
fx_swirl.scale((swirl_fx_frames[0].get_width(),
               swirl_fx_frames[0].get_height()))

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load("assets/imgs/network-red-filled-layer-1-pixelated.png")
bg2 = pygame.image.load("assets/imgs/network-red-filled-layer-2-alt.png")
# tex = engine.surface_to_texture(bg)
# bg = pygame.transform.scale(bg, (const.WIDTH, const.HEIGHT))
logo = pygame.image.load(os.path.join("img", "logo.png")).convert()
logo = pygame.transform.scale(
    logo, (logo.get_width() / 1.5, logo.get_height() / 1.5))

transitions.init(screen, const.WIDTH, const.HEIGHT)
clock = pygame.time.Clock()

padding = 20

small_font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 48)

# bg_color = (176, 174, 167) #B0AEA7
# text_color = (49, 47, 40) #312F28
# text_lightest_color = (125,120,102) #7D7866

# Create TextInput-object
font_input = pygame.font.Font("assets/fonts/ArgentPixelCF-Italic.otf", 42)
textinput = pygame_textinput.TextInputVisualizer(font_object=font_input)
textinput.font_color = text_color
textinput.cursor_width = 2
textinput.cursor_color = text_color
# textinput.cursor_blink_interval = 1000

font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)

# Board layout data
letters = "?ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "
# positions = []

# Layout constants
start_x = 50
start_y = 200
spacing = 28
row_spacing = 60

class Entity(object):
  def __init__(self, x, y, color):
    self.color = color
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(const.VELOCITY, const.VELOCITY)
    self.acceleration = pygame.Vector2(0.5, 0.5)
    self.friction = 0.95

  def Draw(self, buffer, ouija_pos):
    spriteAnim.blit(buffer, (
        ((self.position.x - soul_frames[0].get_width() / 2)) + ouija_pos[0],
        ((self.position.y -
         soul_frames[0].get_height() / 2) - 25 + ouija_pos[1])
    ))

  def Move(self, to: pygame.Vector2):
    target = to
    dir = target - self.position

    if (dir.x == 0 and dir.y == 0):
      return

    self.velocity.x = self.velocity.x * self.friction + \
        self.acceleration.x * dir.normalize().x
    self.velocity.y = self.velocity.y * self.friction + \
        self.acceleration.y * dir.normalize().y
    self.velocity.x = max(-const.MAX_SPEED,
                          min(const.MAX_SPEED, self.velocity.x))
    self.velocity.y = max(-const.MAX_SPEED,
                          min(const.MAX_SPEED, self.velocity.y))
    self.position.x += self.velocity.x
    self.position.y += self.velocity.y

  def Teleport(self, to: pygame.Vector2):
    self.position.x = to.x
    self.position.y = to.y
    return

class Camera:
  def __init__(self):
    self.offset = pygame.Vector2(0, 0)
    self.duration = 0
    self.intensity = 0

  def start_shake(self, duration=6, intensity=3):
    self.duration = duration
    self.intensity = intensity

  def update(self):
    if self.duration > 0:
      self.offset.x = random.randint(-self.intensity, self.intensity)
      self.offset.y = random.randint(-self.intensity, self.intensity)
      self.duration -= 1
    else:
      self.offset = pygame.Vector2(0, 0)

# บว7921


entity = Entity(const.INIT_POINT_X, const.INIT_POINT_Y, const.RED)
camera = Camera()

# Glow data
GLOW_DURATION_FRAMES = 60
GLOW_MAX_ALPHA = 200
GLOW_DURATION = 1  # seconds to fade out

# Glow base surface

# pygame.draw.circle(glow_base, (255, 0, 0), (80, 80), 80)

def get_glow_alpha(frame_left):
  return int(GLOW_MAX_ALPHA * (frame_left / GLOW_DURATION_FRAMES))


def create_radial_glow(size, color=(255, 255, 255), max_alpha=100):
  surface = pygame.Surface((size, size), pygame.SRCALPHA)
  center = size // 2

  for radius in range(center, 0, -1):
    alpha = int(max_alpha * (radius / center)**2)
    pygame.draw.circle(surface, (*color, alpha), (center, center), radius)

  return surface

def create_pixelated_glow(size, color=(255, 255, 255), steps=4, max_alpha=120):
  surface = pygame.Surface((size, size), pygame.SRCALPHA)
  center = size // 2
  max_radius = center

  step_size = max_radius // steps

  for i in range(steps):
    alpha = int(max_alpha * ((steps - i) / steps))
    radius = max_radius - i * step_size
    rect = pygame.Rect(center - radius, center -
                       radius, radius * 2, radius * 2)
    pygame.draw.ellipse(surface, (*color, alpha), rect)

  return surface

def blend_color(start_color, end_color, t):
  return tuple(int(start + (end - start) * t) for start, end in zip(start_color, end_color))


def create_radial_gradient_surface(size, inner_color=(0, 0, 0, 0), outer_color=(0, 0, 0, 255)):
  width, height = size
  surface = pygame.Surface((width, height), pygame.SRCALPHA)
  center_x, center_y = width // 2, height // 2
  max_radius = math.hypot(center_x, center_y)

  for y in range(height):
    for x in range(width):
      dx = x - center_x
      dy = y - center_y
      distance = math.hypot(dx, dy)
      t = min(distance / max_radius, 1.0)  # Normalize 0.0 - 1.0

      # Interpolate between inner and outer color
      r = int(inner_color[0] + (outer_color[0] - inner_color[0]) * t)
      g = int(inner_color[1] + (outer_color[1] - inner_color[1]) * t)
      b = int(inner_color[2] + (outer_color[2] - inner_color[2]) * t)
      a = int(inner_color[3] + (outer_color[3] - inner_color[3]) * t)

      surface.set_at((x, y), (r, g, b, a))

  return surface

# def draw_node(sc, pos):
#   color = 255, 0, 0
#   pygame.draw.circle(sc, color, pos, 20)

def draw_line_with_signal(sc, start, end, progress):
  # pygame.draw.line(sc, (80, 80, 80), start, end, 2)
  if 0 <= progress <= 1:
    x = start[0] + (end[0] - start[0]) * progress
    y = start[1] + (end[1] - start[1]) * progress
    pygame.draw.circle(sc, (255, 255, 255), (int(x), int(y)), 8)



# glow_base = create_radial_glow(160, (255, 0, 0), max_alpha=255)
# glow_base = create_pixelated_glow(160, (255, 0, 0), steps=6, max_alpha=255)
glow_base = create_radial_gradient_surface(
    size=(screen.get_width(), screen.get_height()),
    inner_color=(0, 0, 0, 0),
    outer_color=(255, 0, 0, 180)
)

def start():
  answer_index = 0
  timeout = const.FPS * const.TIMEOUT_FACTOR
  go_to_init_pos = False
  answer = ""
  current_answer = ""
  ouija_pos = None
  glow_frame_counter = 0
  # total_time = 0

  activation_order = []
  activation_index = 0
  signals = []

  border_image = pygame.image.load(
      "assets/ui/hexany/Panels/Transparent/bone_breakers.png").convert_alpha()
  tile_size = 32
  nine = utils.slice_nine(border_image, tile_size)
  panel_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())

  border_image_2 = pygame.image.load(
      "assets/ui/hexany/Panels/Transparent/simple.png").convert_alpha()
  nine_2 = utils.slice_nine(border_image_2, tile_size)
  msg_box_w = screen.get_width() // 2
  msg_box_h = screen.get_height() // 6
  panel_input_msg_box_rect = pygame.Rect(
      screen.get_width() / 2 - (msg_box_w / 2),
      screen.get_height() - (msg_box_h / 2),
      msg_box_w,
      msg_box_h
  )

  for key in nine:
    nine[key] = utils.tint_surface(nine[key], text_color)

  for key in nine_2:
    nine_2[key] = utils.tint_surface(nine_2[key], text_color)

  pygame.key.set_repeat(400, 25)

  while not states.quit_app:
    current_time = pygame.time.get_ticks()
    try:
      reply = states.reply_answer.get(False)
    except queue.Empty:
      reply = None

    if not reply == None and not states.abort:
      answer = reply
      answer = answer.upper()
      to = pygame.Vector2(
          const.CHARACTERS[answer[answer_index]]["pos"][0], const.CHARACTERS[answer[answer_index]]["pos"][1])

    events = pygame.event.get()
    textinput.update(events)

    for event in events:
      if event.type == QUIT:
        pygame.quit()
        sys.exit()
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
          states.is_fullscreen = not states.is_fullscreen
          if states.is_fullscreen:
            pygame.display.set_mode((const.WIDTH, const.HEIGHT))
          else:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
          panel_rect = pygame.Rect(
              0, 0, screen.get_width(), screen.get_height())
        elif event.key == pygame.K_RETURN:
          if textinput.value != "":
            # match commands with prefix (::).
            if val := re.match(r"(;;\S+)(?:\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?))?$", textinput.value):
              cmd = val.group().split(' ')
              if cmd[0] == ";;set_fps":
                try:
                  const.FPS = utils.clamp(10, int(cmd[1]), 60)
                except IndexError:
                  print(
                      "your SET_FPS index is not correct or maybe out of range.")
              elif cmd[0] == ";;set_timeout_factor":
                const.TIMEOUT_FACTOR = float(cmd[1])
              elif cmd[0] == ";;set_move_mode":
                try:
                  const.MOVE_MODE = utils.clamp(1, int(cmd[1]), 2)
                except IndexError:
                  print("SET_MOVE_MODE accept 1 or 2")
              elif cmd[0] == ";;set_max_speed":
                try:
                  const.MAX_SPEED = utils.clamp(1, int(cmd[1]), 200)
                except IndexError:
                  print(
                      "your MAX_SPEED index is not correct or maybe out of range.")
              # elif cmd[0] == "::SET_VELOCITY":
              #     try:
              #         pointer.velocity.x = clamp(1, int(cmd[1]), 10)
              #         pointer.velocity.y = clamp(1, int(cmd[1]), 10)
              #     except IndexError:
              #         print(
              #             "your VELOCITY index is not correct or maybe out of range.")
              elif cmd[0] == ";;stop":
                states.abort = True
                go_to_init_pos = True
                const.TIMEOUT_FACTOR = 2
              elif cmd[0] == ";;bye":
                const.TIMEOUT_FACTOR = 2
                answer = " "
                states.reply_answer.empty()
                states.abort = False
                to = pygame.Vector2(700, 50)
                # pygame.quit()
                # sys.exit()
              # elif cmd[0] == "::BREAK":
                # try:
                #     reply_answer.get(False)
                # except queue.Empty:
                #     continue
                # reply_answer.task_done()
            else:
              # question = const.USER + question.lower() + '\n'
              # question = textinput.value.lower() + '\n'
              _answer = "Are You Ready???????"
              # answer = model.ask(question)
              # mockup_ans = random.choice(
              #     ["I am a ghost, so I don't have a gender."])
              states.reply_answer.put(_answer)
              states.abort = False
              # try:
              #     outFile = open('conversation.txt', 'a')
              #     outFile.write('Q:{}A:{}\n\n'.format(
              #         question, answer))
              #     outFile.close()
              # except IOError as e:
              #     print("I/O error({0.filename}):".format(e))
    camera.update()

    buffer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # if transitions.updateScreen() == False:
    if answer_index <= len(answer) and answer:
      if entity.position.distance_to(to) < 15 + 15:
        timeout -= 1

    if timeout == 0:
      if to == pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
        timeout = const.FPS * const.TIMEOUT_FACTOR
        current_answer = ""
        go_to_init_pos = False
      else:
        activation_order.append(answer[answer_index].upper())
        current_answer += random.choice(
            [answer[answer_index].upper(), answer[answer_index].lower()])
        answer_index += 1
        fx_swirl.play()
        arg.client.send_message("/synth_shot", [const.MOVE_MODE])
        glow_frame_counter = GLOW_DURATION_FRAMES
        
        # camera.start_shake()

        if answer_index < len(answer):
          char = answer[answer_index].upper()
          timeout = const.FPS * const.TIMEOUT_FACTOR
          if const.CHARACTERS.get(char):
            to = pygame.Vector2(
                const.CHARACTERS[char]["pos"][0], const.CHARACTERS[char]["pos"][1])
        else:
          go_to_init_pos = True

    if glow_frame_counter > 0:
      glow_frame_counter -= 1
      blend_t = glow_frame_counter / GLOW_DURATION_FRAMES
      bg_color = blend_color((150, 0, 0), (0, 0, 0), 1 - blend_t)
    else:
      bg_color = (0, 0, 0)

    buffer.fill(bg_color)

    ouija_pos = get_center_position(buffer, (const.WIDTH, const.HEIGHT))
    buffer.blit(bg2, (0+ouija_pos[0], 0+ouija_pos[1]))
    buffer.blit(bg, (0+ouija_pos[0], 0+ouija_pos[1]))

    # if glow_frame_counter > 0:
    #   glow_alpha = get_glow_alpha(glow_frame_counter)
    #   glow_surface = glow_base.copy()
    #   glow_surface = pygame.transform.smoothscale(glow_surface, screen.get_size())
    #   glow_surface.set_alpha(glow_alpha)
    #   buffer.blit(glow_surface, (0, 0))

    # if glow_frame_counter > 0:
    #   glow_alpha = get_glow_alpha(glow_frame_counter)
    #   glow_surface = glow_base.copy()
    #   glow_surface.set_alpha(glow_alpha)
    #   # screen.set_alpha(glow_alpha)
    #   buffer.blit(glow_surface, (
    #     (entity.position.x-(60-ouija_pos[0])),
    #     (entity.position.y-(60-ouija_pos[1]))
    #   ))

    if go_to_init_pos and to != pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
      answer_index = 0
      to = pygame.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y)
      # current_answer = ""
      timeout = const.FPS * const.TIMEOUT_FACTOR

    ghost_msg = pygame.font.Font("assets/fonts/NicerNightie.ttf", 50)
    ghost_msg = ghost_msg.render(str(current_answer), True, const.WHITE)

    # Draw "YES" and "NO"
    yes_text = font.render("Yes", True, text_color)
    no_text = font.render("No", True, text_color)
    buffer.blit(yes_text, (70+ouija_pos[0], 50+ouija_pos[1]))
    buffer.blit(no_text, (240+ouija_pos[0], 50+ouija_pos[1]))

    # Draw "GOODBYE"
    goodbye_text = font.render("Goodbye", True, text_color)
    buffer.blit(goodbye_text, (700+ouija_pos[0], 50 + ouija_pos[1]))

    for _, letter in enumerate(letters):
      if letter == " ":
        display_letter = "(  )"
      else:
        display_letter = letter.lower() if letter.isalpha() else letter
      color = bg_color if display_letter.isalpha() else text_color
      text = small_font.render(f"{display_letter}", True, color)
      pos = [const.CHARACTERS[letter]["pos"][0] + ouija_pos[0],
             const.CHARACTERS[letter]["pos"][1] + ouija_pos[1]]
      buffer.blit(text, pos)

    utils.draw_text(
        buffer,
        current_answer,
        const.RED,
        [70 + ouija_pos[0], 130+ouija_pos[1], 805, 78*4],
        pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
    )

    if (answer):
      if (const.MOVE_MODE == 1):
        entity.Move(to)
        if answer_index > 0:
          fx_swirl.blit(buffer, (
              ((const.CHARACTERS[answer[answer_index - 1]]["pos"][0] -
                swirl_fx_frames[0].get_width() / 2) + 10) + ouija_pos[0],
              ((const.CHARACTERS[answer[answer_index - 1]]["pos"][1] -
                swirl_fx_frames[0].get_height() / 2) + 10) + ouija_pos[1]
          ))
      elif (const.MOVE_MODE == 2):
        entity.Teleport(to)

    entity.Draw(buffer, ouija_pos)
    arg.client.send_message(
        "/synth_coord", [entity.position.x / const.WIDTH, 1.0 - entity.position.y / const.HEIGHT])

    panel_input_msg_box_rect.width = screen.get_width() / 2
    panel_input_msg_box_rect.x = (screen.get_width() / 2 - ouija_pos[0]) - 90
    panel_input_msg_box_rect.y = screen.get_height() - ouija_pos[1]

    buffer.blit(textinput.surface, (panel_input_msg_box_rect.x +
                25, panel_input_msg_box_rect.y + 14))

    # draw_nine_slice_scaled(
    #     nine_2, WINDOW, panel_input_msg_box_rect, tile_size, 2)

    screen.fill((0, 0, 0))
    screen.blit(buffer, camera.offset)
    utils.draw_nine_slice_scaled(nine, screen, panel_rect, tile_size, 2)

    # === Draw nodes and static connections ===
    if activation_index < len(activation_order):
      node_id = activation_order[activation_index]
      # nodes[node_id]["activated"] = True
      start_pos = const.CHARACTERS[node_id]["pos"]

      for target_id in const.CHARACTERS[node_id]["nodes"]:
        end_pos = const.CHARACTERS[target_id]["pos"]
        end_pos_offset = (-22,35) if target_id == "O" else (-22,20)
        signals.append({
            "start": (start_pos[0] + 35 + ouija_pos[0], start_pos[1] + 24+ ouija_pos[1]),
            "end": (end_pos[0] + end_pos_offset[0] + ouija_pos[0], end_pos[1] + end_pos_offset[1] + ouija_pos[1]),
            "start_time": current_time,
            "duration": 400
        })

      activation_index += 1
    
    new_signals = []
    for sig in signals:
      elapsed = current_time - sig["start_time"]
      progress = elapsed / sig["duration"]

      if progress < 1.0:
        draw_line_with_signal(screen, sig["start"], sig["end"], progress)
        new_signals.append(sig)
      else:
        # Reached the target — light it up!
        for node_id, data in const.CHARACTERS.items():
          end_pos_offset = (22,-35) if node_id == "O" else (22,-20)
          # revert offset to compare with const.CHARACTERS
          end_sig_pos = (sig["end"][0] + end_pos_offset[0] + -ouija_pos[0], sig["end"][1] + end_pos_offset[1] + -ouija_pos[1])
          if data["pos"] == end_sig_pos:
            # data["activated"] = True
            activation_order.append(node_id.upper())
            # activation_index += 1
            arg.client.send_message("/synth_shot_nodes", [])
            break
    signals = new_signals

    # ================================================

    pygame.display.update()
    clock.tick(const.FPS)


def main():
  screen.fill(bg_color)
  if transitions.updateScreen() == False:
    if states.should_start:
      start()
