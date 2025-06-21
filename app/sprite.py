import pygame
from external import pyganim

class FXSprite(pygame.sprite.Sprite):
  def __init__(self, animation: pyganim.PygAnimation, position, total_duration):
    super().__init__()
    self.animation = animation  
    self.position = position
    self.started = False

    self.image = pygame.Surface(position, pygame.SRCALPHA)
    self.rect = self.image.get_rect(center=position)

    self.timer = 0  # Keep track of time
    self.frame_duration = total_duration

  def start(self):
    self.animation.play()
    self.started = True
    self.image: pygame.Surface = self.animation.getCurrentFrame()
    self.rect = self.image.get_rect(center=self.position)

  def update(self, dt):
    if not self.started:
      return
    
    self.animation.blit(self.image, self.position) 
    self.image: pygame.Surface = self.animation.getCurrentFrame()
    self.rect = self.image.get_rect(center=self.position)

    self.timer += dt
    if self.timer >= self.frame_duration:
      self.kill()
