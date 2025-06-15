import re
from . import transitions
from . import states
from . import arg
from . import const
from . import utils
from . import pyganim
from easing_functions import *
from pygame.locals import *
import queue
import pygame
import pygame_textinput
# from pygame_render import RenderEngine
import sys
import os
import random

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

bg_color = (0, 0, 0)  # B0AEA7
text_color = (255, 0, 0)  # 312F28
text_lightest_color = (255, 255, 255)  # 7D7866

pygame.init()
WINDOW = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

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
soul_frames = [pygame.image.load(path).convert_alpha() for path in soul_frame_paths]

spriteAnim = pyganim.PygAnimation([(frame, 0.1) for frame in soul_frames])
spriteAnim.scale((soul_frames[0].get_width() * 5, soul_frames[0].get_height() * 5))
spriteAnim.play()


# Load swirl effect frames dynamically and apply color replacement
swirl_fx_frame_paths = [
  f"assets/sprites/swirl/frame_{i:02d}.png" for i in range(17)
]
swirl_fx_frames = [pygame.image.load(path).convert_alpha() for path in swirl_fx_frame_paths]

replace_color_swirl_fx_frames = [
  utils.replace_color(frame, text_color, text_lightest_color, tolerance=0)
  for frame in swirl_fx_frames
]

fx_swirl = pyganim.PygAnimation(
  [(frame, 0.1) for frame in replace_color_swirl_fx_frames],
  loop=False
)
fx_swirl.scale((swirl_fx_frames[0].get_width(), swirl_fx_frames[0].get_height()))

os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption("live-ghosting")
bg = pygame.image.load("assets/imgs/network-red-filled-layer-1-pixelated.png")
bg2 = pygame.image.load("assets/imgs/network-red-filled-layer-2-alt.png")
# tex = engine.surface_to_texture(bg)
# bg = pygame.transform.scale(bg, (const.WIDTH, const.HEIGHT))
logo = pygame.image.load(os.path.join("img", "logo.png")).convert()
logo = pygame.transform.scale(
    logo, (logo.get_width() / 1.5, logo.get_height() / 1.5))
coin = pygame.image.load(os.path.join(
    "img", "coin-sm-shadow2.png")).convert_alpha()

transitions.init(WINDOW, const.WIDTH, const.HEIGHT)
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

  def Draw(self, ouija_pos):
    spriteAnim.blit(WINDOW, (
        ((self.position.x - coin.get_width() / 2) + 10) + ouija_pos[0],
        ((self.position.y - coin.get_height() / 2) + ouija_pos[1])
    ))

  def Move(self, to: pygame.Vector2):
    target = to
    dir = target - self.position

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


entity = Entity(const.INIT_POINT_X, const.INIT_POINT_Y, const.RED)

def start():
  answer_index = 0
  timeout = const.FPS * const.TIMEOUT_FACTOR
  go_to_init_pos = False
  answer = ""
  current_answer = ""
  ouija_pos = None
  total_time = 0

  border_image = pygame.image.load(
      "assets/ui/hexany/Panels/Transparent/bone_breakers.png").convert_alpha()
  tile_size = 32
  nine = utils.slice_nine(border_image, tile_size)
  panel_rect = pygame.Rect(0, 0, WINDOW.get_width(), WINDOW.get_height())

  border_image_2 = pygame.image.load(
      "assets/ui/hexany/Panels/Transparent/simple.png").convert_alpha()
  nine_2 = utils.slice_nine(border_image_2, tile_size)
  msg_box_w = WINDOW.get_width() // 2
  msg_box_h = WINDOW.get_height() // 6
  panel_input_msg_box_rect = pygame.Rect(
      WINDOW.get_width() / 2 - (msg_box_w / 2),
      WINDOW.get_height() - (msg_box_h / 2),
      msg_box_w,
      msg_box_h
  )

  for key in nine:
    nine[key] = utils.tint_surface(nine[key], text_color)

  for key in nine_2:
    nine_2[key] = utils.tint_surface(nine_2[key], text_color)

  while not states.quit_app:
    try:
      reply = states.reply_answer.get(False)
    except queue.Empty:
      reply = None

    if not reply == None and not states.abort:
      answer = reply
      answer = answer.upper()
      to = pygame.Vector2(
          const.CHARACTERS[answer[answer_index]][0], const.CHARACTERS[answer[answer_index]][1])

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
              0, 0, WINDOW.get_width(), WINDOW.get_height())
        elif event.key == pygame.K_RETURN:
          if textinput.value != "":
            # match commands with prefix (::).
            if val := re.match("^((::).[A-z]+) *\d*", textinput.value):
              cmd = val.group().split(' ')
              if cmd[0] == "::SET_FPS":
                try:
                  const.FPS = utils.clamp(10, int(cmd[1]), 60)
                except IndexError:
                  print(
                      "your SET_FPS index is not correct or maybe out of range.")
              elif cmd[0] == "::SET_TIMEOUT_FACTOR":
                try:
                  const.TIMEOUT_FACTOR = utils.clamp(1, int(cmd[1]), 8)
                except IndexError:
                  print(
                      "your TIMEOUT_FACTOR index is not correct or maybe out of range.")
              elif cmd[0] == "::SET_MAX_SPEED":
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
              elif cmd[0] == "::STOP":
                states.abort = True
                go_to_init_pos = True
              elif cmd[0] == "::BYE":
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

    WINDOW.fill(bg_color)
    
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
        current_answer += random.choice([answer[answer_index].upper(), answer[answer_index].lower()])
        answer_index += 1
        fx_swirl.play()
        arg.client.send_message("/synth_shot", [])

        if answer_index < len(answer):
          char = answer[answer_index].upper()
          timeout = const.FPS * const.TIMEOUT_FACTOR
          if const.CHARACTERS.get(char):
            to = pygame.Vector2(
                const.CHARACTERS[char][0], const.CHARACTERS[char][1])
        else:
          go_to_init_pos = True

    ouija_pos = get_center_position(WINDOW, (const.WIDTH, const.HEIGHT))
    WINDOW.blit(bg2, (0+ouija_pos[0], 0+ouija_pos[1]))
    WINDOW.blit(bg, (0+ouija_pos[0], 0+ouija_pos[1]))
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
    WINDOW.blit(yes_text, (70+ouija_pos[0], 50+ouija_pos[1]))
    WINDOW.blit(no_text, (240+ouija_pos[0], 50+ouija_pos[1]))

    # Draw "GOODBYE"
    goodbye_text = font.render("Goodbye", True, text_color)
    WINDOW.blit(goodbye_text, (700+ouija_pos[0], 50 + ouija_pos[1]))

    for _, letter in enumerate(letters):
      if letter == " ":
        display_letter = "(  )"
      else:
        display_letter = letter.lower() if letter.isalpha() else letter
      color = bg_color if display_letter.isalpha() else text_color
      text = small_font.render(f"{display_letter}", True, color)
      pos = [const.CHARACTERS[letter][0] + ouija_pos[0],
             const.CHARACTERS[letter][1] + ouija_pos[1]]
      WINDOW.blit(text, pos)

    utils.draw_text(
        WINDOW,
        current_answer, 
        const.RED,
        [70 + ouija_pos[0], 130+ouija_pos[1], 805, 78*4],
        pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
    )

    if (answer):
      entity.Move(to)
      if answer_index > 0:
        fx_swirl.blit(WINDOW, (
            ((const.CHARACTERS[answer[answer_index - 1]][0] -
             swirl_fx_frames[0].get_width() / 2) + 10) + ouija_pos[0],
            ((const.CHARACTERS[answer[answer_index - 1]][1] -
             swirl_fx_frames[0].get_height() / 2) + 10) + ouija_pos[1]
        ))

    entity.Draw(ouija_pos)
    arg.client.send_message(
        "/synth_coord", [entity.position.x / const.WIDTH, 1.0 - entity.position.y / const.HEIGHT])

    panel_input_msg_box_rect.width = WINDOW.get_width() / 2
    panel_input_msg_box_rect.x = (WINDOW.get_width() / 2 - ouija_pos[0]) - 90
    panel_input_msg_box_rect.y = WINDOW.get_height() - ouija_pos[1]

    WINDOW.blit(textinput.surface, (panel_input_msg_box_rect.x +
                25, panel_input_msg_box_rect.y + 14))

    utils.draw_nine_slice_scaled(nine, WINDOW, panel_rect, tile_size, 2)
    # draw_nine_slice_scaled(
    #     nine_2, WINDOW, panel_input_msg_box_rect, tile_size, 2)

    # Clear the screen
    # engine.clear(64, 128, 64)
    # total_time += clock.get_time()
    # shader_glow['time'] = total_time
    # engine.render(tex, engine.screen, scale=16., shader=shader_glow)

    pygame.display.update()
    clock.tick(const.FPS)


def main():
  WINDOW.fill(bg_color)
  if transitions.updateScreen() == False:
    if states.should_start:
      start()
