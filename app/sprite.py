import pygame
from external import pyganim

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
    self.angle = -direction.angle_to(pygame.Vector2(1, 0))
  
  def _update_frame(self):
    current_frame = self.animation.getCurrentFrame()
    rotated_image = pygame.transform.rotate(current_frame, self.angle)
    self.image = rotated_image
    self.rect = self.image.get_rect(center=self.position)