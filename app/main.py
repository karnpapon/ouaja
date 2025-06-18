from . import const
from . import utils
from . import pyganim
from easing_functions import *
from pygame.locals import *
import pygame
import pygame_textinput
import sys
import os
from .scene import SceneManager, GameScene, MenuScene 
from .entity import Entity
from .camera import Camera
from functools import partial

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'

font_input_intro = pygame.font.Font("assets/fonts/NicerNightie.ttf", 58)
textinput_intro = pygame_textinput.TextInputVisualizer(font_object=font_input_intro)
textinput_intro.font_color = const.TEXT_COLOR
textinput_intro.cursor_width = 2
textinput_intro.cursor_color = const.TEXT_COLOR

def main():
  pygame.init()
  pygame.display.set_caption("-")
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
      [(frame, 0.05) for frame in replace_color_swirl_fx_frames],
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
  textinput_intro = pygame_textinput.TextInputVisualizer(
      font_object=font_input_intro)
  textinput_intro.font_color = const.TEXT_COLOR
  textinput_intro.cursor_width = 2
  textinput_intro.cursor_color = const.TEXT_COLOR

  entity = Entity(const.INIT_POINT_X, const.INIT_POINT_Y,
                  const.RED, spriteAnim, soul_frames[0])
  camera = Camera()

  manager = SceneManager(screen, clock)

  total_duration_swirl_fx_frames = 6000

  def switch_to_game():
    manager.switch_to(partial(GameScene, camera=camera,
                      entity=entity, textinput=textinput, fx_swirl=fx_swirl, total_duration_swirl_fx_frames=total_duration_swirl_fx_frames))

  manager.switch_to(lambda mngr: MenuScene(mngr, switch_to_game, textinput_intro))
  # switch_to_game()

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
