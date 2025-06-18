from . import const
from . import utils
from . import pyganim
from easing_functions import *
from pygame.locals import *
import pygame
import pygame_textinput
import sys
import os
import random
from . import screen as screen_manager
from functools import partial

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.init()
pygame.display.set_caption("ouaja")
screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

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
    utils.replace_color(frame, const.TEXT_COLOR,
                        const.TEXT_LIGHTEST_COLOR, tolerance=0)
    for frame in swirl_fx_frames
]

fx_swirl = pyganim.PygAnimation(
    [(frame, 0.1) for frame in replace_color_swirl_fx_frames],
    loop=False
)
fx_swirl.scale((swirl_fx_frames[0].get_width(),
               swirl_fx_frames[0].get_height()))

clock = pygame.time.Clock()

font_input = pygame.font.Font("assets/fonts/ArgentPixelCF-Italic.otf", 42)
textinput = pygame_textinput.TextInputVisualizer(font_object=font_input)
textinput.font_color = const.TEXT_COLOR
textinput.cursor_width = 2
textinput.cursor_color = const.TEXT_COLOR

font_input_intro = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
textinput_intro = pygame_textinput.TextInputVisualizer(font_object=font_input_intro)
textinput_intro.font_color = const.TEXT_COLOR
textinput_intro.cursor_width = 2
textinput_intro.cursor_color = const.TEXT_COLOR

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

entity = Entity(const.INIT_POINT_X, const.INIT_POINT_Y, const.RED)
camera = Camera()

def main():
  manager = screen_manager.ScreenManager(screen)

  def switch_to_game():
    manager.switch_to(partial(screen_manager.GameScreen, camera=camera,
                      entity=entity, textinput=textinput, fx_swirl=fx_swirl))

  manager.switch_to(partial(screen_manager.MenuScreen,
                    switch_to_game=switch_to_game, textinput=textinput_intro))

  running = True
  while running:
    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT:
        running = False

    manager.handle_events(events)
    manager.update()
    manager.draw()

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main()
