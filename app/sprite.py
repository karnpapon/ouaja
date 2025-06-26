import pygame
from external import pyganim
from typing import List
from . import utils

class SpriteSheet:
  def __init__(self, filename):
    self.sheet = pygame.image.load(filename).convert_alpha()

  def get_frame(self, x, y, width, height):
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    frame.blit(self.sheet, (0, 0), pygame.Rect(x, y, width, height))
    return frame

  def get_strip(self, start_x, start_y, frame_width, frame_height, num_frames, spacing=0):
    frames: List[pygame.Surface] = []
    for i in range(num_frames):
      x = start_x + i * (frame_width + spacing)
      frame = self.get_frame(x, start_y, frame_width, frame_height)
      frames.append(frame)
    return frames

class AnimationFactory:
  def __init__(self, sprite_sheet: SpriteSheet):
    self.sheet = sprite_sheet

  def create_animation_strip(self, x, y, width, height, count, duration=0.1, spacing=0, scale=1.0, tint_color=None, loop=True):
    frames = self.sheet.get_strip(x, y, width, height, count, spacing)
    if scale != 1.0:
      scaled_size = (int(width * scale), int(height * scale))
      frames = [
          pygame.transform.scale(frame, scaled_size)
          for frame in frames
      ]
      if tint_color:
        frames = [utils.tint_surface(frame, tint_color) for frame in frames]

    anim_frames = [(frame, duration) for frame in frames]
    return pyganim.PygAnimation(anim_frames, loop=loop)

class FXSprite(pygame.sprite.Sprite):
  def __init__(self, animation: pyganim.PygAnimation, position: pygame.Vector2, total_duration):
    super().__init__()
    self.animation = animation
    self.position = position
    self.position_to = pygame.Vector2(0)
    self.started = False

    self.image = pygame.Surface(position, pygame.SRCALPHA)
    self.rect = self.image.get_rect(center=position)

    self.timer = 0  # Keep track of time
    self.frame_duration = total_duration
    self.angle = 0

  def start(self):
    self.animation.play()
    self.started = True
    self.image: pygame.Surface = self.animation.getCurrentFrame()
    self.rect = self.image.get_rect(center=self.position)
    self._update_frame()

  def update(self, dt):
    if not self.started:
      return
    self._update_frame()
    self.timer += dt
    if self.timer >= self.frame_duration:
      self.kill()

  def set_rotation_towards(self, target_point: pygame.Vector2):
    direction = target_point - self.position
    self.to_point = target_point
    self.angle = direction.angle_to(pygame.Vector2(1, 0))

  def _update_frame(self):
    current_frame = self.animation.getCurrentFrame()
    rotated_image = pygame.transform.rotate(current_frame, self.angle)
    self.image = rotated_image
    self.rect = self.image.get_rect(center=self.position)
