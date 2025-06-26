from . import const
from pygame.locals import *
import pygame
import sys
import os
from .scene import SceneManager, GameScene, IntroScene 

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
# os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'

def main():
  pygame.init()
  pygame.display.set_caption("-")
  pygame.mouse.set_visible(False) 
  screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
  clock = pygame.time.Clock()

  scene_manager = SceneManager()
  main_menu_scene = IntroScene()
  scene_manager.push(main_menu_scene)
  
  # input_stream = InputStream()
  running = True
  while running:
    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT:
        running = False

    # input_stream.processInput()
    if scene_manager.is_empty(): running = False
    scene_manager.input(events)
    scene_manager.update(events)
    scene_manager.draw(screen)

    clock.tick(60)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main()
