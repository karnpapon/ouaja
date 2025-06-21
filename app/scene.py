import sys
import pygame
import pygame_textinput
import re
import ast
import random
import queue
import threading
from . import states
from . import const
from . import utils
from . import arg
from external import pyganim
from .entity import Entity
from .camera import Camera
from .model import conversation_with_summary

response = None
fetching = False

# match commands with prefix (;;).
command_prefix_pattern = r"(;;\S+)(?:\s+(?:([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)|\(\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\)))?"
command_prefix_pattern_cursor = r"(;\S+)(?:\s+(?:([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)|\(\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\)))?"

def write_file(_question, _response):
  try:
    outFile = open('conversation.txt', 'a')
    outFile.write('Q:{}A:{}\n\n'.format(
        _question, _response))
    outFile.close()
  except IOError as e:
    print("I/O error({0.filename}):".format(e))

def ask(question):
  text = f"{question}"
  response = conversation_with_summary.predict(input=text)  # "i'm here now"
  states.reply_answer.put(response)
  write_file(question, response)


def start_fetch_thread(question):
  fetch_thread = threading.Thread(target=ask, args=(question,))
  fetch_thread.start()

class SceneManager:
  def __init__(self):
    self.scenes = []

  def isEmpty(self):
    return len(self.scenes) == 0

  def enterScene(self):
    if len(self.scenes) > 0:
      scene = self.scenes[-1]
      if not scene.setup_done:
        scene.setup()
        scene.setup_done = True
      scene.on_enter()

  def exitScene(self):
    if len(self.scenes) > 0:
      self.scenes[-1].on_exit()

  def input(self, event):
    if len(self.scenes) > 0:
      self.scenes[-1].handle_events(self, event)

  def update(self, events):
    if len(self.scenes) > 0:
      self.scenes[-1].update(self, events)

  def draw(self, screen):
    if len(self.scenes) > 0:
      self.scenes[-1].draw(self, screen)
    pygame.display.flip()

  def push(self, scene):
    self.exitScene()
    self.scenes.append(scene)
    self.enterScene()

  def pop(self):
    self.exitScene()
    self.scenes.pop()
    self.enterScene()

  def set(self, scenes):
    while len(self.scenes) > 0:
      self.pop()
    for s in scenes:
      self.push(s)

class BaseScene:
  def __init__(self):
    # Load soul animation frames dynamically
    soul_frame_paths = [
        f"assets/sprites/soul/soul_{i}.png" for i in range(1, 9)
    ]
    soul_frames = [pygame.image.load(path).convert_alpha()
                   for path in soul_frame_paths]

    player_sprites = pyganim.PygAnimation(
        [(frame, 0.1) for frame in soul_frames])
    player_sprites.scale((soul_frames[0].get_width() * 5,
                          soul_frames[0].get_height() * 5))
    player_sprites.play()

    entity = Entity(const.INIT_POINT_X, const.INIT_POINT_Y,
                    const.RED, player_sprites, soul_frames[0])

    self.entity = entity
    self.setup_done = False

  def on_enter(self): pass
  def on_exit(self): pass
  def handle_events(self, sm, events): pass
  def setup(self): pass
  def update(self, sm, events): pass
  def draw(self, sm, screen): pass

class MenuScene(BaseScene):
  def __init__(self):
    super().__init__()

    font_input_intro = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
    text_input = pygame_textinput.TextInputVisualizer(
        font_object=font_input_intro)
    text_input.font_color = const.TEXT_COLOR
    text_input.cursor_width = 12
    text_input.cursor_color = const.TEXT_COLOR

    self.delay_counter = 0
    self.request_accepted = False
    self.font = font_input_intro
    self.textinput = text_input
    pygame.key.set_repeat(400, 25)

  def on_enter(self): pass
  def on_exit(self): pass
  def setup(self): pass

  def handle_events(self, sm: SceneManager, events):
    self.textinput.update(events)
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
          self.panel_rect = pygame.Rect(
              0, 0, pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
        elif event.key == pygame.K_RETURN:
          if self.textinput.value != "":
            if self.textinput.value.lower() == const.OPENING_SENTENCE.lower():
              self.request_accepted = True
              arg.client.send_message("/synth_shot_opening", [])

  def update(self, sm, events): pass

  def draw(self, sm, screen: pygame.Surface):
    screen.fill((0, 0, 0))
    title = self.font.render(const.OPENING_SENTENCE, True, (255, 0, 0))
    if (self.delay_counter == 100):
      sm.push(FadeTransitionScene([self], [GameScene()]))

    if (self.request_accepted):
      self.delay_counter += 1
      self.entity.spawn(screen, (
          (screen.get_width() / 2) -
          (self.entity.soul_frames.get_width() / 2) - 60,
          (screen.get_height() / 2) - (self.entity.soul_frames.get_height() / 2) - 80)
      )
    screen.blit(self.textinput.surface, ((screen.get_width(
    ) // 2 - (title.get_width() // 2)), (screen.get_height() // 2)))

class GameScene(BaseScene):
  def __init__(self):
    super().__init__()
    # Load swirl effect frames dynamically and apply color replacement
    swirl_fx_frame_paths = [
        f"assets/sprites/swirl/frame_{i:02d}.png" for i in range(17)
    ]
    swirl_fx_frames = [pygame.image.load(
        path).convert_alpha() for path in swirl_fx_frame_paths]

    replace_color_swirl_fx_frames = [
        utils.replace_color(frame, const.TEXT_COLOR,
                            const.TEXT_LIGHTEST_COLOR, tolerance=0)
        for frame in swirl_fx_frames
    ]

    fx_swirl = pyganim.PygAnimation(
        [(frame, 0.05) for frame in replace_color_swirl_fx_frames],
        loop=False
    )
    fx_swirl.scale((swirl_fx_frames[0].get_width(),
                    swirl_fx_frames[0].get_height()))

    camera = Camera()

    font_input = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
    text_input = pygame_textinput.TextInputVisualizer(font_object=font_input)
    text_input.font_color = const.TEXT_COLOR
    text_input.cursor_width = 12
    text_input.cursor_color = const.TEXT_COLOR

    self.player_pos = [100, 100]
    self.font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
    self.small_font = pygame.font.Font("assets/fonts/NicerNightie.ttf", 48)
    self.camera = camera
    self.fx_swirl = fx_swirl
    self.textinput = text_input
    self.haunted_last_call_time = 0
    self.haunted_interval = 200  # ms
    self.haunted_rand_lower_bound = 50
    self.haunted_rand_upper_bound = 1000

  def on_enter(self): pass
  def on_exit(self): pass

  def handle_events(self, sm, events):
    self.textinput.update(events)
    if re.match(command_prefix_pattern_cursor, self.textinput.value):
      self.textinput.cursor_color = const.WHITE
    else:
      self.textinput.cursor_color = const.RED

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
          self.panel_rect = pygame.Rect(
              0, 0, pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
        elif event.key == pygame.K_RETURN:
          if self.textinput.value != "":
            if val := re.match(command_prefix_pattern, self.textinput.value):
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
              elif cmd[0] == ";;set_trigger_mode":
                try:
                  const.TRIGGER_MODE = utils.clamp(0, int(cmd[1]), 1)
                except IndexError:
                  print("TRIGGER_MODE accept 0 or 1")
              elif cmd[0] == ";;set_haunted_mode":
                const.HAUNTED_MODE = utils.clamp(0, int(cmd[1]), 1)
                self.answer = " "
              elif cmd[0] == ";;set_haunted_mode_lower_bound":
                self.haunted_rand_lower_bound = utils.clamp(
                    20, int(cmd[1]), 49)
                self.answer = " "
              elif cmd[0] == ";;set_haunted_mode_upper_bound":
                self.haunted_rand_upper_bound = utils.clamp(
                    50, int(cmd[1]), 1000)
                self.answer = " "
              elif cmd[0] == ";;move_to":
                const.HAUNTED_MODE = False
                const.TRIGGER_MODE = False
                move_to = ast.literal_eval(cmd[1])
                self.to = pygame.Vector2(move_to)
                self.answer = " "
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
                const.HAUNTED_MODE = False
                const.TRIGGER_MODE = True
                const.TIMEOUT_FACTOR = 2
              elif cmd[0] == ";;bye":
                const.TIMEOUT_FACTOR = 2
                self.answer = " "
                states.reply_answer.empty()
                states.abort = False
                self.to = pygame.Vector2(700, 50)
            else:
              question = self.textinput.value.lower() + '\n'
              start_fetch_thread(question)
              states.abort = False

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
    self.all_sprites = pygame.sprite.Group()
    self.to = pygame.Vector2(0)

    self.border_image = pygame.image.load(
        "assets/ui/hexany/Panels/Transparent/bone_breakers.png").convert_alpha()
    self.tile_size = 32
    self.nine = utils.slice_nine(self.border_image, self.tile_size)
    self.panel_rect = pygame.Rect(
        0, 0, pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])

    self.border_image_2 = pygame.image.load(
        "assets/ui/hexany/Panels/Transparent/simple.png").convert_alpha()
    self.nine_2 = utils.slice_nine(self.border_image_2, self.tile_size)
    self.msg_box_w = pygame.display.get_window_size()[0] // 2
    self.msg_box_h = pygame.display.get_window_size()[1] // 6
    self.panel_input_msg_box_rect = pygame.Rect(
        pygame.display.get_window_size()[0] / 2 - (self.msg_box_w / 2),
        pygame.display.get_window_size()[1] - (self.msg_box_h / 2),
        self.msg_box_w,
        self.msg_box_h
    )

    for key in self.nine:
      self.nine[key] = utils.tint_surface(self.nine[key], const.TEXT_COLOR)

    for key in self.nine_2:
      self.nine_2[key] = utils.tint_surface(self.nine_2[key], const.TEXT_COLOR)

    pygame.key.set_repeat(400, 25)

  def update(self, sm, events): pass

  def draw(self, sm, screen: pygame.Surface):
    current_time = pygame.time.get_ticks()
    try:
      reply = states.reply_answer.get(False)
    except queue.Empty:
      reply = None

    if not reply == None and not states.abort:
      self.answer = reply
      self.answer = self.answer.upper()
      self.to = pygame.Vector2(
          const.CHARACTERS[self.answer[self.answer_index]]["pos"][0],
          const.CHARACTERS[self.answer[self.answer_index]]["pos"][1])

    self.camera.update()
    buffer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    ouija_pos = utils.get_center_position(buffer, (const.WIDTH, const.HEIGHT))

    if self.answer_index <= len(self.answer) and self.answer:
      if self.entity.position.distance_to(self.to) < 15 + 15:
        self.timeout -= 1

    if self.timeout == 0:
      if self.to == pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
        self.timeout = const.FPS * const.TIMEOUT_FACTOR
        self.current_answer = ""
        self.go_to_init_pos = False
      else:
        if const.ACTIVATE_NODES:
          self.activation_order.append(self.answer[self.answer_index].upper())
        self.current_answer += random.choice(
            [self.answer[self.answer_index].upper(),
             self.answer[self.answer_index].lower(),
             self.answer[self.answer_index].lower(),
             self.answer[self.answer_index].lower(),
             self.answer[self.answer_index].lower(),
             ])

        # fx_anim = self.fx_swirl.getCopy()
        # fx_sprite = FXSprite(fx_anim, (
        #     ((const.CHARACTERS[self.answer[self.answer_index - 1]]["pos"][0] -
        #         self.fx_swirl.getFrame(0).get_width() / 2) + 10) + ouija_pos[0],
        #     ((const.CHARACTERS[self.answer[self.answer_index - 1]]["pos"][1] -
        #         self.fx_swirl.getFrame(0).get_height() / 2) + 10) + ouija_pos[1]
        # ), self.total_duration_swirl_fx_frames)
        self.fx_swirl.play()
        # self.all_sprites.add(fx_sprite)

        if (const.TRIGGER_MODE and not const.HAUNTED_MODE):
          arg.client.send_message(
              "/synth_shot", [const.MOVE_MODE, self.answer[self.answer_index]])
        self.glow_frame_counter = const.GLOW_DURATION_FRAMES

        if (not const.HAUNTED_MODE):
          self.answer_index += 1

        # self.camera.start_shake()

        if self.answer_index < len(self.answer):
          char = self.answer[self.answer_index].upper()
          self.timeout = const.FPS * const.TIMEOUT_FACTOR
          if const.CHARACTERS.get(char):
            self.to = pygame.Vector2(
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
    buffer.blit(self.bg2, (0+ouija_pos[0], 0+ouija_pos[1]))
    buffer.blit(self.bg, (0+ouija_pos[0], 0+ouija_pos[1]))

    if (const.HAUNTED_MODE and current_time - self.haunted_last_call_time >= self.haunted_interval):
      self.to = pygame.math.Vector2(
          random.uniform(0, pygame.display.get_window_size()[0]),
          random.uniform(0, pygame.display.get_window_size()[1])
      )
      if (random.choice([0, 1])):
        self.camera.start_shake()
      self.haunted_interval = random.uniform(
          self.haunted_rand_lower_bound, self.haunted_rand_upper_bound)
      self.haunted_last_call_time = current_time

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

    if self.go_to_init_pos and self.to != pygame.math.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y):
      self.answer_index = 0
      self.to = pygame.Vector2(const.INIT_POINT_X, const.INIT_POINT_Y)
      # self.current_answer = ""
      self.timeout = const.FPS * const.TIMEOUT_FACTOR

    ghost_msg = pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
    ghost_msg = ghost_msg.render(str(self.current_answer), True, const.RED)

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

    _text_rect = ghost_msg.get_rect()
    _text_rect.centerx = screen.get_width() // 2
    _text_rect.centery = 138+ouija_pos[1]

    buffer.blit(ghost_msg, _text_rect)

    # utils.draw_text(
    #     buffer,
    #     self.current_answer,
    #     const.WHITE,
    #     [70 + ouija_pos[0], 130+ouija_pos[1], 805, 78*4],
    #     pygame.font.Font("assets/fonts/NicerNightie.ttf", 62)
    # )

    if (self.answer):
      if (const.MOVE_MODE == 1):
        self.entity.move(self.to)
        if self.answer_index > 0:
          # self.all_sprites.update(current_time)
          # self.all_sprites.draw(buffer)
          _char_data = const.CHARACTERS.get(self.answer[self.answer_index - 1])
          if _char_data is not None:
            self.fx_swirl.blit(buffer, (
                ((_char_data["pos"][0] -
                  self.fx_swirl.getFrame(0).get_width() / 2) + 10) + ouija_pos[0],
                ((_char_data["pos"][1] -
                  self.fx_swirl.getFrame(0).get_height() / 2) + 10) + ouija_pos[1]
            ))
      elif (const.MOVE_MODE == 2):
        self.entity.teleport(self.to)

    self.entity.draw(buffer, ouija_pos)
    arg.client.send_message(
        "/synth_coord", [self.entity.position.x / const.WIDTH, 1.0 - self.entity.position.y / const.HEIGHT])

    self.panel_input_msg_box_rect.width = screen.get_width() / 2
    self.panel_input_msg_box_rect.x = (
        (screen.get_width() / 2) - ouija_pos[0]) - 90
    self.panel_input_msg_box_rect.y = screen.get_height() - ouija_pos[1]

    buffer.blit(self.textinput.surface, (self.panel_input_msg_box_rect.x +
                25, self.panel_input_msg_box_rect.y + 14))

    # draw_nine_slice_scaled(
    #     nine_2, WINDOW, panel_input_msg_box_rect, tile_size, 2)

    screen.fill((0, 0, 0))
    screen.blit(buffer, self.camera.offset)
    utils.draw_nine_slice_scaled(
        self.nine, screen, self.panel_rect, self.tile_size, 2)

    # === Draw nodes and static connections ===
    if const.ACTIVATE_NODES:
      if self.activation_index < len(self.activation_order):
        node_id = self.activation_order[self.activation_index]
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

        self.activation_index += 1

      new_signals = []
      for sig in self.signals:
        elapsed = current_time - sig["start_time"]
        progress = elapsed / sig["duration"]

        if progress < 1.0:
          utils.draw_line_with_signal(
              screen, sig["start"], sig["end"], progress)
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
              if (const.TRIGGER_MODE):
                arg.client.send_message("/synth_shot_nodes", [])
              break
      self.signals = new_signals

class TransitionScene(BaseScene):
  def __init__(self, fromScenes, toScenes):
    super().__init__()
    self.current_percentage = 0
    self.from_scenes = fromScenes
    self.to_scenes = toScenes

  def update(self, sm, events):
    self.current_percentage += 2
    if self.current_percentage >= 100:
      sm.pop()
      for s in self.to_scenes:
        sm.push(s)
    for scene in self.from_scenes:
      scene.update(sm, events)
    if len(self.to_scenes) > 0:
      for scene in self.to_scenes:
        scene.setup()
        scene.update(sm, events)
    else:
      if len(sm.scenes) > 1:
        sm.scenes[-2].update(sm, events)

class FadeTransitionScene(TransitionScene):
  def draw(self, sm, screen: pygame.Surface):
    if self.current_percentage < 50:
      for s in self.from_scenes:
        s.draw(sm, screen)
    else:
      if len(self.to_scenes) == 0:
        if len(sm.scenes) > 1:
          sm.scenes[-2].draw(sm, screen)
      else:
        for s in self.to_scenes:
          s.draw(sm, screen)

    # fade overlay
    overlay = pygame.Surface((screen.get_size()[0], screen.get_size()[1]))
    alpha = int(abs((255 - ((255/50)*self.current_percentage))))
    overlay.set_alpha(255 - alpha)
    overlay.fill(const.BG_COLOR)
    screen.blit(overlay, (0, 0))
