import pygame
import random
from math import sin, tan, cos
from .sprite import FXSprite, SpriteSheet, AnimationFactory

class Firefly():
  def __init__(self, screen_w, screen_h):
    ff_sheet = SpriteSheet("assets/sprites/firefly.png")
    ff_anim_factory = AnimationFactory(ff_sheet)
    ff_sprite = ff_anim_factory.create_animation_strip(
        0, random.choice([0, 16]), 16, 16, 4, duration=0.2, scale=4.0)
    ff_sprite.play()
    self.x = random.randint(0, screen_w)
    self.y = random.randint(0, screen_h)
    self.y_pos_offset = random.randint(1, screen_h)
    self.x_pos_offset = random.randint(1, screen_w)
    self.sprite = ff_sprite
    self.angle = random.uniform(0, 2 * 3.14159)
    self.speed = random.uniform(20, 40)  # pixels per second
    self.turn_speed = random.uniform(0.5, 1.5)  # how fast it can turn
    self.randomize_props()

  def randomize_props(self):
    self.r = random.randint(6, 16)
    self.pulse = random.randint(6, 14)  # determines the radius of the blink
    self.offset = random.randint(1, 10)  # offsets the blink pattern timing
    self.vel_x = self.rand_vel(10, 20)
    self.vel_y = self.rand_vel(10, 20)
    self.y_pos_sin_scale = random.randint(20, 150)
    self.y_sin_offset = random.randint(10, 20)

  def rand_vel(self, low, high):  # returns random velocity
    num = random.randint(low, high)
    if random.randint(0, 1):
      return -num
    return num

  def update_radius(self, time_elapsed, freq_scale=1):
    # noise = random.uniform(-0.5, 0.5)
    self.r = (sin((time_elapsed + self.offset) * freq_scale)) 

  def update_pos_firefly(self, time_elapsed, delta_t, screen_w, screen_h):
    # Random turning
    # self.angle += random.uniform(-self.turn_speed, self.turn_speed) * delta_t
    self.angle += 0.5 * delta_t
    self.speed += random.uniform(-2, 2) * delta_t
    self.speed = max(10, min(self.speed, 50))  # Clamp speed

    # Movement vector
    dx = self.speed * cos(self.angle) * delta_t
    dy = self.speed * sin(self.angle) * delta_t

    self.x += dx
    self.y += dy

    # Wrap screen
    if self.x - self.r > screen_w:
        self.x = -self.r
    elif self.x + self.r < 0:
        self.x = screen_w + self.r

    if self.y - self.r > screen_h:
        self.y = -self.r
    elif self.y + self.r < 0:
        self.y = screen_h + self.r

  def draw(self, screen: pygame.Surface, time_elapsed):
    if self.r > 0:
      self.sprite.blit(screen,[self.x, self.y])
