import struct
import pygame
import os
import sys
from pygame.locals import *

import moderngl


def resource_path(relative):
  if hasattr(sys, "_MEIPASS"):
    absolute_path = os.path.join(sys._MEIPASS, relative)
  else:
    absolute_path = os.path.join(relative)
  return absolute_path


class GraphicEngine:
  def __init__(self, screen, VIRTUAL_RES=(800, 600), style=1, cpu_only=False, fullscreen=False):
    pygame.init()
    self.VIRTUAL_RES = VIRTUAL_RES
    self.cpu_only = cpu_only
    self.screen = screen
    self.fullscreen = fullscreen

    if self.cpu_only:
      self.display = pygame.display.get_surface()
      return

    self.ctx = moderngl.create_context()
    self.style = style

    self.texture_coordinates = [0, 0, 1, 0, 0, 1, 1, 1]
    self.world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]
    self.render_indices = [0, 1, 2, 1, 2, 3]

    # Load shaders
    with open(resource_path("assets/shaders/screen_vertex.glsl"), "r") as vs_file:
      vertex_shader_source = vs_file.read()
    with open(resource_path("assets/shaders/screen_fragment.glsl"), "r") as fs_file:
      fragment_shader_source = fs_file.read()

    self.prog = self.ctx.program(
      vertex_shader=vertex_shader_source,
      fragment_shader=fragment_shader_source,
    )

    # Create screen texture
    self.screen_texture = self.ctx.texture(
        self.VIRTUAL_RES, 3,
        pygame.image.tostring(screen, "RGB", False)
    )
    self.screen_texture.repeat_x = False
    self.screen_texture.repeat_y = False

    # Load resources
    self.dither_tex = self.load_texture("imgs/bayer-tile.png")
    self.color_tex = self.load_texture("imgs/palette-br.png")

    # Bind textures
    self.dither_tex.use(location=0)
    self.color_tex.use(location=1)
    self.screen_texture.use(location=2)

    # Set uniforms
    self.prog["u_dither_tex"] = 0
    self.prog["u_color_tex"] = 1
    self.prog["u_screen_tex"] = 2

    self.prog["u_bit_depth"].value = 26
    self.prog["u_contrast"].value = 1.5
    self.prog["u_offset"].value = 0.5
    self.prog["u_dither_size"].value = 1.0

    # Setup geometry
    self.vbo = self.ctx.buffer(struct.pack('8f', *self.world_coordinates))
    self.uvmap = self.ctx.buffer(struct.pack('8f', *self.texture_coordinates))
    self.ibo = self.ctx.buffer(struct.pack('6I', *self.render_indices))

    self.vao_content = [
        (self.vbo, '2f', 'vert'),
        (self.uvmap, '2f', 'in_text'),
    ]
    self.vao = self.ctx.vertex_array(
        self.prog, self.vao_content, index_buffer=self.ibo)

  def load_texture(self, relative_path, components=3, mode='RGB'):
    path = os.path.join("assets", relative_path)
    surface = pygame.image.load(path).convert()
    surface = pygame.transform.flip(surface, False, True)
    data = pygame.image.tostring(surface, mode)
    tex = self.ctx.texture(surface.get_size(), components, data)
    tex.build_mipmaps()
    return tex

  def render(self):
    if self.cpu_only:
      self.display.blit(self.screen, (0, 0))
      pygame.display.update()
      return

    # self.screen.fill((255, 0, 0))
    texture_data = pygame.image.tostring(self.screen, "RGB", True)
    self.screen_texture.write(texture_data)

    # self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
    self.vao.render()
    pygame.display.flip()

  def set_fullscreen(self, REAL_RES):
    flags = pygame.DOUBLEBUF | (pygame.OPENGL if not self.cpu_only else 0)
    if self.fullscreen:
      flags |= pygame.FULLSCREEN
    pygame.display.set_mode(REAL_RES, flags)

  def __call__(self):
    self.render()
