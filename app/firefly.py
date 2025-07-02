import pygame
import random
from math import sin, tan

# MIN_VEL = 10
# MAX_VEL = 40
# BLACK = (0,0,0)
# WHITE = (255,255,255)
# YELLOW = (250, 240, 0)
# FIREFLY_YELLOW = (250, 254, 50)
# FIREFLY_ORANGE = (250, 210, 10)

class Firefly():
  def __init__(self, screen_w, screen_h):
    self.x = random.randint(0, screen_w)
    self.y = random.randint(0, screen_h)
    self.y_pos_offset = random.randint(1, screen_h)
    self.randomize_props()

  def randomize_props(self):
    self.r = random.randint(6, 16)
    self.pulse = random.randint(6, 14)  # determines the radius of the blink
    self.offset = random.randint(1, 10)  # offsets the blink pattern timing
    self.vel_x = self.rand_vel(20, 50)
    self.vel_y = self.rand_vel(20, 50)
    self.y_pos_sin_scale = random.randint(50, 250)
    self.y_sin_offset = random.randint(1, 10)

  def rand_vel(self, low, high):  # returns random velocity
    num = random.randint(low, high)
    if random.randint(0, 1):
      return -num
    return num

  def update_radius(self, time_elapsed, freq_scale=1):
    self.r = sin((time_elapsed+self.offset)*freq_scale) * self.pulse

  def update_pos_linear(self, time_elapsed, delta_t, screen_w, screen_h):
    self.x += self.vel_x * delta_t
    self.y += self.vel_y * delta_t

    if self.x - self.r > screen_w:  # checks right side
      self.x = -self.r

    elif self.x <= -self.r:
      self.x = screen_w + self.r

    if self.y + self.r <= 0:  # checks top
      self.y = screen_h + self.r

    elif self.y - self.r >= screen_h:
      self.y = -self.r

  def update_pos_rng(self, time_elapsed, delta_t, screen_w, screen_h):
    self.x += (self.vel_x) * delta_t
    self.y = sin(time_elapsed + self.y_sin_offset) * \
        self.y_pos_sin_scale + self.y_pos_offset

    if self.x - self.r > screen_w:  # checks right side
      self.x = -self.r

    elif self.x <= -self.r:
      self.x = screen_w + self.r

    if self.y + self.r <= 0:  # checks top
      self.y = screen_h + self.r

    elif self.y - self.r >= screen_h:
      self.y = -self.r

  def draw(self, screen, time_elapsed):
    if self.r > 0:
      # pygame.draw.circle(screen, FIREFLY_ORANGE, [self.x, self.y], self.r+2, 2)
      pygame.draw.circle(screen, (255,0,0), [self.x, self.y], self.r)
