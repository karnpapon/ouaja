import pygame
from . import const

class Entity(object):
  def __init__(self, x, y, color, spriteAnim: pygame.Surface, soul_frames: pygame.Surface):
    self.color = color
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(const.VELOCITY, const.VELOCITY)
    self.acceleration = pygame.Vector2(0.5, 0.5)
    self.friction = 0.95
    self.sprite_anim = spriteAnim
    self.soul_frames = soul_frames
    # self.sprite_anim.set_alpha(0)

  def spawn(self, buffer, pos):
    self.sprite_anim.blit(buffer, pos)

  def draw(self, buffer, ouija_pos):
    self.sprite_anim.blit(buffer, (
        ((self.position.x - self.soul_frames.get_width() / 2)) + ouija_pos[0] + 20,
        ((self.position.y -
         self.soul_frames.get_height() / 2) - 25 + ouija_pos[1])
    ))

  def move(self, to: pygame.Vector2):
    target = to
    dir = target - self.position

    if (dir.x == 0 and dir.y == 0):
      return

    self.velocity.x = self.velocity.x * self.friction + \
        self.acceleration.x * dir.normalize().x
    self.velocity.y = self.velocity.y * self.friction + \
        self.acceleration.y * dir.normalize().y
    self.velocity.x = max(-const.MAX_SPEED,
                          min(const.MAX_SPEED, self.velocity.x))
    self.velocity.y = max(-const.MAX_SPEED,
                          min(const.MAX_SPEED, self.velocity.y))
    self.position.x += self.velocity.x
    self.position.y += self.velocity.y

  def teleport(self, to: pygame.Vector2):
    self.position.x = to.x
    self.position.y = to.y
    return