from . import const
from pygame.locals import *
import pygame
import sys
import os
import math
from .scene import SceneManager, GameScene, IntroScene 
from .shaders import GraphicEngine

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
# os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'

DEBUG = os.getenv("DEBUG", False)

def main():
  pygame.init()
  
  if DEBUG:
    # Set OpenGL context attributes for macOS compatibility
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
  
  pygame.display.set_caption("-")
  pygame.mouse.set_visible(False) 
  screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT), flags=pygame.NOFRAME) # pygame.NOFRAME / pygame.DOUBLEBUF | pygame.OPENGL
  clock = pygame.time.Clock()

  scene_manager = SceneManager()
  intro_scene = IntroScene()
  game_scene = GameScene()
  scene_manager.push(intro_scene)

  # crt_shader = GraphicEngine(screen, VIRTUAL_RES=(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1]), style=1, fullscreen=True)
  # crt_shader.set_fullscreen((const.WIDTH, const.HEIGHT))

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
    
    # crt_shader.render()
    clock.tick(60)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main()
