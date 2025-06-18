import pygame
import random

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