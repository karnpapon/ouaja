import sys
import pygame
import re
import ast
import random
import queue
from . import states
from . import const
from . import utils
from . import arg
from . import pyganim

class ScreenManager:
  def __init__(self, screen):
    self.screen = screen
    self.current_screen = None

  def switch_to(self, screen_factory):
    self.current_screen = screen_factory(self)
    self.current_screen.setup()

  def handle_events(self, events):
    self.current_screen.handle_events(events)

  def update(self):
    self.current_screen.update()

  def draw(self):
    self.current_screen.draw()


class BaseScreen:
  def __init__(self, manager: ScreenManager):
    self.manager = manager
    self.screen = manager.screen

  def handle_events(self, events, screen): pass
  def setup(self): pass
  def update(self): pass
  def draw(self, screen): pass


class MenuScreen(BaseScreen):
  def __init__(self, manager, switch_to_game):
    super().__init__(manager)
    self.button_rect = pygame.Rect(300, 350, 200, 60)
    self.font = pygame.font.SysFont(None, 48)
    self.switch_to_game = switch_to_game

  def handle_events(self, events):
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if self.button_rect.collidepoint(event.pos):
          self.switch_to_game()

  def setup(self): pass
  def update(self): pass

  def draw(self):
    self.screen.fill((30, 30, 30))
    title = self.font.render(const.OPENING_SENTENCE, True, (255, 255, 255))
    self.screen.blit(title, (400 - title.get_width() // 2, 150))
    pygame.draw.rect(self.screen, (0, 200, 0), self.button_rect)
    pygame.draw.rect(self.screen, (255, 255, 255), self.button_rect, 3)
    label = self.font.render("Start Game", True, (0, 0, 0))
    self.screen.blit(label, (
        self.button_rect.centerx - label.get_width() // 2,
        self.button_rect.centery - label.get_height() // 2
    ))

class GameScreen(BaseScreen):
  def __init__(
      self,
      manager: ScreenManager,
      camera,
      entity,
      textinput,
      fx_swirl: pyganim.PygAnimation
  ):
    super().__init__(manager)
    self.player_pos = [100, 100]
    self.font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
    self.small_font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 48)
    self.camera = camera
    self.fx_swirl = fx_swirl
    self.textinput = textinput
    self.entity = entity

  def handle_events(self, events):
    for event in events:
      if event.type == pygame.QUIT:
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
              0, 0, self.screen.get_width(), self.screen.get_height())
        elif event.key == pygame.K_RETURN:
          if self.textinput.value != "":
            # match commands with prefix (::).
            if val := re.match(r"(;;\S+)(?:\s+(?:([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)|\(\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\)))?", self.textinput.value):
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
                  print("MOVE_MODE accept 1 or 2")
              elif cmd[0] == ";;move_to":
                move_to = ast.literal_eval(cmd[1])
                to = pygame.Vector2(move_to)
                answer = " "
              elif cmd[0] == ";;set_activate_nodes":
                try:
                  const.ACTIVATE_NODES = utils.clamp(0, int(cmd[1]), 1)
                  if int(cmd[1]) == 0:
                    self.activation_order.clear()
                except IndexError:
                  print("ACTIVATE_NODES accept 0 or 1")
              elif cmd[0] == ";;set_max_speed":
                try:
                  const.MAX_SPEED = utils.clamp(1, int(cmd[1]), 200)
                except IndexError:
                  print(
                      "your MAX_SPEED index is not correct or maybe out of range.")
              elif cmd[0] == ";;stop":
                states.abort = True
                self.go_to_init_pos = True
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

  def setup(self):
    self.timeout = const.FPS * const.TIMEOUT_FACTOR
    self.go_to_init_pos = False
    self.answer = ""
    self.current_answer = ""
    self.ouija_pos = None
    self.glow_frame_counter = 0
    self.letters = "?ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "
    self.bg = pygame.image.load(
        "assets/imgs/network-red-filled-layer-1-pixelated.png")
    self.bg2 = pygame.image.load(
        "assets/imgs/network-red-filled-layer-2-alt.png")

    self.activation_order = []
    self.activation_index = 0
    self.signals = []
    self.answer_index = 0

    self.border_image = pygame.image.load(
        "assets/ui/hexany/Panels/Transparent/bone_breakers.png").convert_alpha()
    self.tile_size = 32
    self.nine = utils.slice_nine(self.border_image, self.tile_size)
    self.panel_rect = pygame.Rect(
        0, 0, self.screen.get_width(), self.screen.get_height())

    self.border_image_2 = pygame.image.load(
        "assets/ui/hexany/Panels/Transparent/simple.png").convert_alpha()
    self.nine_2 = utils.slice_nine(self.border_image_2, self.tile_size)
    self.msg_box_w = self.screen.get_width() // 2
    self.msg_box_h = self.screen.get_height() // 6
    self.panel_input_msg_box_rect = pygame.Rect(
        self.screen.get_width() / 2 - (self.msg_box_w / 2),
        self.screen.get_height() - (self.msg_box_h / 2),
        self.msg_box_w,
        self.msg_box_h
    )

    for key in self.nine:
      self.nine[key] = utils.tint_surface(self.nine[key], const.TEXT_COLOR)

    for key in self.nine_2:
      self.nine_2[key] = utils.tint_surface(self.nine_2[key], const.TEXT_COLOR)

    pygame.key.set_repeat(400, 25)

  def update(self): pass

  def draw(self):
    current_time = pygame.time.get_ticks()
    try:
      reply = states.reply_answer.get(False)
    except queue.Empty:
      reply = None

    if not reply == None and not states.abort:
      self.answer = reply
      self.answer = self.answer.upper()
      to = pygame.Vector2(
          const.CHARACTERS[self.answer[self.answer_index]]["pos"][0],
          const.CHARACTERS[self.answer[self.answer_index]]["pos"][1])

    events = pygame.event.get()
    self.textinput.update(events)

    self.camera.update()
    buffer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

    if self.answer_index <= len(self.answer) and self.answer:
      if self.entity.position.distance_to(to) < 15 + 15:
        self.timeout -= 1

    if self.timeout == 0:
      if to == pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
        self.timeout = const.FPS * const.TIMEOUT_FACTOR
        self.current_answer = ""
        self.go_to_init_pos = False
      else:
        if const.ACTIVATE_NODES:
          self.activation_order.append(self.answer[self.answer_index].upper())
        self.current_answer += random.choice(
            [self.answer[self.answer_index].upper(), self.answer[self.answer_index].lower()])
        self.answer_index += 1
        self.fx_swirl.play()
        arg.client.send_message("/synth_shot", [const.MOVE_MODE])
        self.glow_frame_counter = const.GLOW_DURATION_FRAMES

        # camera.start_shake()

        if self.answer_index < len(self.answer):
          char = self.answer[self.answer_index].upper()
          self.timeout = const.FPS * const.TIMEOUT_FACTOR
          if const.CHARACTERS.get(char):
            to = pygame.Vector2(
                const.CHARACTERS[char]["pos"][0], const.CHARACTERS[char]["pos"][1])
        else:
          self.go_to_init_pos = True

    if self.glow_frame_counter > 0:
      self.glow_frame_counter -= 1
      blend_t = self.glow_frame_counter / const.GLOW_DURATION_FRAMES
      bg_color = utils.blend_color((150, 0, 0), (0, 0, 0), 1 - blend_t)
    else:
      bg_color = (0, 0, 0)

    buffer.fill(bg_color)

    ouija_pos = utils.get_center_position(buffer, (const.WIDTH, const.HEIGHT))
    buffer.blit(self.bg2, (0+ouija_pos[0], 0+ouija_pos[1]))
    buffer.blit(self.bg, (0+ouija_pos[0], 0+ouija_pos[1]))

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

    if self.go_to_init_pos and to != pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
      self.answer_index = 0
      to = pygame.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y)
      # self.current_answer = ""
      self.timeout = const.FPS * const.TIMEOUT_FACTOR

    ghost_msg = pygame.font.Font("assets/fonts/NicerNightie.ttf", 50)
    ghost_msg = ghost_msg.render(str(self.current_answer), True, const.WHITE)

    # Draw "YES" and "NO"
    yes_text = self.font.render("Yes", True, const.TEXT_COLOR)
    no_text = self.font.render("No", True, const.TEXT_COLOR)
    buffer.blit(yes_text, (70+ouija_pos[0], 50+ouija_pos[1]))
    buffer.blit(no_text, (240+ouija_pos[0], 50+ouija_pos[1]))

    # Draw "GOODBYE"
    goodbye_text = self.font.render("Goodbye", True, const.TEXT_COLOR)
    buffer.blit(goodbye_text, (700+ouija_pos[0], 50 + ouija_pos[1]))

    for _, letter in enumerate(self.letters):
      if letter == " ":
        display_letter = "(  )"
      else:
        display_letter = letter.lower() if letter.isalpha() else letter
      color = bg_color if display_letter.isalpha() else const.TEXT_COLOR
      text = self.small_font.render(f"{display_letter}", True, color)
      pos = [const.CHARACTERS[letter]["pos"][0] + ouija_pos[0],
             const.CHARACTERS[letter]["pos"][1] + ouija_pos[1]]
      buffer.blit(text, pos)

    utils.draw_text(
        buffer,
        self.current_answer,
        const.RED,
        [70 + ouija_pos[0], 130+ouija_pos[1], 805, 78*4],
        pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
    )

    if (self.answer):
      if (const.MOVE_MODE == 1):
        self.entity.Move(to)
        if self.answer_index > 0:
          self.fx_swirl.blit(buffer, (
              ((const.CHARACTERS[self.answer[self.answer_index - 1]]["pos"][0] -
                self.fx_swirl.getFrame(0).get_width() / 2) + 10) + ouija_pos[0],
              ((const.CHARACTERS[self.answer[self.answer_index - 1]]["pos"][1] -
                self.fx_swirl.getFrame(0).get_height() / 2) + 10) + ouija_pos[1]
          ))
      elif (const.MOVE_MODE == 2):
        self.entity.Teleport(to)

    self.entity.Draw(buffer, ouija_pos)
    arg.client.send_message(
        "/synth_coord", [self.entity.position.x / const.WIDTH, 1.0 - self.entity.position.y / const.HEIGHT])

    self.panel_input_msg_box_rect.width = self.screen.get_width() / 2
    self.panel_input_msg_box_rect.x = (
        self.screen.get_width() / 2 - ouija_pos[0]) - 90
    self.panel_input_msg_box_rect.y = self.screen.get_height() - ouija_pos[1]

    buffer.blit(self.textinput.surface, (self.panel_input_msg_box_rect.x +
                25, self.panel_input_msg_box_rect.y + 14))

    # draw_nine_slice_scaled(
    #     nine_2, WINDOW, panel_input_msg_box_rect, tile_size, 2)

    self.screen.fill((0, 0, 0))
    self.screen.blit(buffer, self.camera.offset)
    utils.draw_nine_slice_scaled(
        self.nine, self.screen, self.panel_rect, self.tile_size, 2)

    # === Draw nodes and static connections ===
    if const.ACTIVATE_NODES:
      if activation_index < len(self.activation_order):
        node_id = self.activation_order[activation_index]
        # nodes[node_id]["activated"] = True
        start_pos = const.CHARACTERS[node_id]["pos"]

        for target_id in const.CHARACTERS[node_id]["nodes"]:
          end_pos = const.CHARACTERS[target_id]["pos"]
          end_pos_offset = (-22, 35) if target_id == "O" else (-22, 20)
          self.signals.append({
              "start": (start_pos[0] + 35 + ouija_pos[0], start_pos[1] + 24 + ouija_pos[1]),
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
          utils.draw_line_with_signal(
              self.screen, sig["start"], sig["end"], progress)
          new_signals.append(sig)
        else:
          # Reached the target — light it up!
          for node_id, data in const.CHARACTERS.items():
            end_pos_offset = (22, -35) if node_id == "O" else (22, -20)
            # revert offset to compare with const.CHARACTERS
            end_sig_pos = (sig["end"][0] + end_pos_offset[0] + -ouija_pos[0],
                           sig["end"][1] + end_pos_offset[1] + -ouija_pos[1])
            if data["pos"] == end_sig_pos:
              # data["activated"] = True
              self.activation_order.append(node_id.upper())
              # activation_index += 1
              arg.client.send_message("/synth_shot", [])
              break
      signals = new_signals
