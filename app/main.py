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

  scene_manager = SceneManager()
  main_menu_scene = MenuScene(textinput_intro)
  scene_manager.push(main_menu_scene)
  
  # input_stream = InputStream()
  running = True
  while running:
    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT:
        running = False

    # input_stream.processInput()
    if scene_manager.isEmpty(): running = False
    scene_manager.input(events)
    scene_manager.update(events)
    scene_manager.draw(screen)

    clock.tick(60)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main()
