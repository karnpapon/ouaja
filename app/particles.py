import pygame
import math
import sys
import random


def direction_average(direction_1, direction_2, ratio):
  direction = math.atan2(
      math.sin(direction_1) * ratio + math.sin(direction_2) * (1 - ratio),
      math.cos(direction_1) * ratio + math.cos(direction_2) * (1 - ratio))
  return direction

def dist_between_points(a, b):
  return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

class particle_class:
  def __init__(self, position, velocity, direction, colour, size, lifetime,
               width=0,
               path_type={"size": "linear", "velocity": "linear"},
               glow={"size": 0, "rings_num": 0, "colour": (0, 0, 0)},
               shape=0,
               previous_position_cap=0,
               desired_vector=None,
               desired_position=None,
               looping=False):
    self.starting_pos = position
    self.pos = position
    self.starting_vel = velocity
    self.vel = velocity
    self.starting_dir = direction
    self.dir = direction
    self.looping = looping

    self.desired_vector = desired_vector
    self.desired_position = desired_position

    self.col = colour
    self.size = size
    self.current_size = size
    self.width = width
    if self.width == 0 and shape == 3:
      self.width = 1

    self.lifetime = lifetime
    self.current_lifetime = lifetime

    self.path_type = path_type  # linear, accelerate, decelerate
    self.glow = glow
    self.shape = shape  # circle 0, square 1, shard 2, snake 3

    self.previous_position_cap = previous_position_cap
    self.previous_positions = [[position[0], position[1]],
                               [position[0], position[1]],
                               [position[0], position[1]]]

  def die(self):
    pass

  def update(self, desired_position_update=None):
    # lifetime percentage
    lifetime_percentage = (self.current_lifetime / self.lifetime)

    # looping
    if self.looping:
      mult = ((self.starting_pos[0] + self.starting_pos[1]) % 2) * 2 - 1
      self.dir += (self.vel / 10) * mult

    # update position
    lifetime_vel = self.vel
    if self.path_type["velocity"] == "accelerate":
      lifetime_vel = self.vel * (-lifetime_percentage + 1)
    elif self.path_type["velocity"] == "decelerate":
      lifetime_vel = self.vel * lifetime_percentage
    self.pos[0] += math.cos(self.dir) * lifetime_vel
    self.pos[1] += math.sin(self.dir) * lifetime_vel

    # update desired vector
    if self.desired_vector != None:
      average_mult = 0.99

      desired_vector = [0, 0]

      desired_vector[0] = self.desired_vector[0]
      desired_vector[1] = self.desired_vector[1]

      average_x = ((math.cos(self.dir) * lifetime_vel) -
                   (math.cos(desired_vector[0]) * desired_vector[1])) * average_mult
      average_y = ((math.sin(self.dir) * lifetime_vel) -
                   (math.sin(desired_vector[0]) * desired_vector[1])) * average_mult

      final_x = (math.cos(desired_vector[0]) * desired_vector[1]) + average_x
      final_y = (math.sin(desired_vector[0]) * desired_vector[1]) + average_y

      self.dir = math.atan2(final_y, final_x)
      self.vel = math.sqrt(final_x ** 2 + final_y ** 2)

    # update desired position
    if desired_position_update != None:
      self.desired_position = desired_position_update

    if self.desired_position != None:
      desired_angle = math.atan2(self.desired_position[1] - self.pos[1],
                                 self.desired_position[0] - self.pos[0])
      ratio_increase = 0.04 * \
          (self.starting_vel - self.vel / self.starting_vel)
      self.dir = direction_average(
          self.dir, desired_angle, 0.95 + ratio_increase)
      self.vel += 0.1

      if dist_between_points(self.pos, self.desired_position) <= int(self.vel * 0.8):
        return True

    # update size
    lifetime_size = lifetime_percentage * self.size
    if self.path_type["size"] == "decelerate":
      lifetime_size = (lifetime_percentage ** 2) * self.size
    elif self.path_type["size"] == "accelerate":
      lifetime_size = (-(lifetime_percentage - 1)**2 + 1) * self.size
    self.current_size = lifetime_size

    # update previous positions
    self.previous_positions.append([self.pos[0], self.pos[1]])
    if len(self.previous_positions) > self.previous_position_cap:
      self.previous_positions.pop(0)

    # update lifetime
    self.current_lifetime -= 1
    if self.current_lifetime <= 0:
      self.die()
      return True
    return False

  def draw(self, surf, camera_offset=[0, 0]):
    pos = (self.pos[0] - camera_offset[0],
           self.pos[1] - camera_offset[1])

    if self.shape == 1:  # drawing a square particle
      pygame.draw.rect(surf,
                       self.col,
                       ((pos[0], pos[1]),
                        (self.current_size, self.current_size)),
                       width=self.width)

    elif self.shape == 2:  # drawing a shard
      dir_offset = [math.cos(self.dir),
                    math.sin(self.dir)]
      perp_offset = [math.cos(self.dir + (math.pi / 2)),
                     math.sin(self.dir + (math.pi / 2))]
      shard_size = self.current_size * (self.current_size / self.size)
      points = ((pos[0] + (dir_offset[0] * shard_size ** 1.2 * 2),
                 pos[1] + (dir_offset[1] * shard_size ** 1.2 * 2)),
                (pos[0] + (perp_offset[0] * shard_size * 0.5),
                 pos[1] + (perp_offset[1] * shard_size * 0.5)),
                (pos[0] - (dir_offset[0] * shard_size ** 1.2 * 2),
                 pos[1] - (dir_offset[1] * shard_size ** 1.2 * 2)),
                (pos[0] - (perp_offset[0] * shard_size * 0.5),
                 pos[1] - (perp_offset[1] * shard_size * 0.5)))
      pygame.draw.polygon(surf,
                          self.col,
                          points,
                          width=self.width)

    elif self.shape == 3:  # drawing a line from previous positions (trail)
      for index, pos in enumerate(self.previous_positions):
        if index != 0:
          width = int(((index + 1) / len(self.previous_positions))
                      * self.current_size)
          pygame.draw.line(surf,
                           self.col,
                           self.previous_positions[index-1],
                           pos,
                           width)
      pygame.draw.circle(surf, self.col,
                         self.previous_positions[-1],
                         self.current_size / 3)

    else:  # drawing a circle particle
      pygame.draw.circle(surf,
                         self.col,
                         [pos[0],
                          pos[1]],
                         self.current_size,
                         width=self.width)

def click_particles(particles, position, colours=[(200, 200, 200), (0, 0, 200)]):
  for i in range(2):
    direction = math.radians(random.randint(0, 360))
    particles.append(particle_class(
        [position[0] + 3 * math.cos(direction),
         position[1] + 3 * math.sin(direction)],
        random.randint(10, 30) / 100,
        direction,
        colours[1],
        3,
        60,
        path_type={"size": "linear", "velocity": "decelerate"},
        shape=2
    ))

  particles.append(particle_class(
      [position[0], position[1]],
      0,
      0,
      colours[1],
      12,
      6
  ))
  particles.append(particle_class(
      [position[0], position[1]],
      0,
      0,
      colours[0],
      10,
      4
  ))

def sparks_particles(particles, position, colour=(200, 200, 200), glow=(10, 10, 0)):
  for size in range(2):
    direction = math.radians(random.randint(-30 - 30 * size,
                                            30 + 30 * size))
    for i in range(2):
      direction_mult = (i * 2) - 1
      particles.append(particle_class(
          [position[0], position[1]],
          4 * direction_mult,
          direction,
          colour,
          5 + 5 * size,
          10,
          path_type={"size": "decelerate", "velocity": "decelerate"},
          glow={"size": 15, "rings_num": 8, "colour": glow},
          shape=2
      ))

def sparks_particles_small(particles, position, colour=(200, 200, 200), glow=(10, 10, 0)):
  for size in range(2):
    direction = math.radians(random.randint(-30 - 30 * size,
                                            30 + 30 * size))
    for i in range(2):
      direction_mult = (i * 2) - 1
      particles.append(particle_class(
          [position[0], position[1]],
          4 * direction_mult,
          direction,
          colour,
          3 + 3 * size,
          10,
          path_type={"size": "decelerate", "velocity": "decelerate"},
          glow={"size": 15, "rings_num": 8, "colour": glow},
          shape=2
      ))

def firefly_particle(particles, position, size, colour=(200, 200, 200), glow=(255, 0, 0), rings_num=4, velocity=0.1):
  particles.append(particle_class(
      position,
      velocity,
      1,
      colour,
      size,
      100000,
      glow={"size": 20, "rings_num": rings_num, "colour": glow},
      shape=1,
      looping=True,
  ))

def apply_glow(surf, size, colour, rings_num, position, mult=1):
  glow_size = size * mult
  pos = [position[0], position[1]]

  glow_surf = pygame.Surface((glow_size * 2, glow_size * 2))
  pygame.draw.circle(glow_surf, colour, (glow_size, glow_size), glow_size)

  for i in range(rings_num):
    ring_size = (glow_size * 2) * ((i + 1) / rings_num)
    surf.blit(pygame.transform.scale(glow_surf, (ring_size, ring_size)),
              (pos[0] - ring_size / 2,
               pos[1] - ring_size / 2),
              special_flags=pygame.BLEND_RGB_ADD)

def add_shadows(surf: pygame.Surface, colour=(250, 250, 250), offset=[1, 1]):
  shadow_surf = pygame.Surface((surf.get_width(), surf.get_height()))
  shadow_surf.set_colorkey((0, 0, 0))

  mask = pygame.mask.from_surface(surf)
  mask_surf = mask.to_surface()
  mask_surf.set_colorkey((0, 0, 0))
  mask_surf.fill(colour, special_flags=pygame.BLEND_RGB_MULT)

  shadow_surf.blit(mask_surf, (offset[0], offset[1]))
  shadow_surf.blit(surf, (0, 0))

  return shadow_surf


if __name__ == "__main__":
  screen_size = (600, 600)
  zoom = 2
  sim_size = [int(num / zoom) for num in screen_size]
  screen = pygame.display.set_mode(screen_size)
  pygame.display.set_caption("particles testing")

  running = True
  clock = pygame.time.Clock()

  game_surf = pygame.Surface(sim_size)
  particle_surf = pygame.Surface(sim_size)
  particle_surf.set_colorkey((0, 0, 0))

  particle_list = []
  mouse_particle_list = []
  mos_pos = [0, 0]

  global_timer = 0

  while running:
    game_surf.fill((0, 0, 0))
    particle_surf.fill((0, 0, 0))
    global_timer += 1

    # mos_pos
    mos_pos = [num / zoom for num in pygame.mouse.get_pos()]
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          click_particles(particle_list, mos_pos, colours=[
                          (200, 200, 200), (172, 107, 38)])
          sparks_particles(particle_list, mos_pos)

    if global_timer % 60 == 0:
      for i in range(10):
        mouse_particle_list.append(particle_class(
            [100, 200],
            random.randint(5, 10) / 10,
            math.radians(random.randint(0, 360)),
            (250, 250, 250),
            random.randint(25, 35)/8,
            3000,
            desired_position=mos_pos,
            shape=3,
            previous_position_cap=30,
        ))

    if global_timer % 60 == 0:
      for i in range(10):
        particle_list.append(particle_class(
            [100, 100],
            random.randint(5, 10) / 10,
            math.radians(random.randint(-120, -60)),
            (100, 100, 150),
            random.randint(25, 35)/10,
            120,
            desired_vector=(math.pi/2, 3)
        ))

    if global_timer % 60 == 0:
      sparks_particles(particle_list, (200, 200))

    if global_timer % 60 == 0:
      click_particles(particle_list, (150, 100))

    if global_timer % 3 == 0:
      for i in range(1):
        particle_list.append(particle_class(
            [200, 100],
            random.randint(5, 15) / 10,
            math.radians(random.randint(-100, -90)),
            (150, 100, 80),
            random.randint(35, 55)/10,
            60,
            glow={"size": 10, "rings_num": 4, "colour": (10, 0, 0)},
            path_type={"size": "decelerate", "velocity": "decelerate"}
        ))

    # updating particles
    for index, particle in sorted(enumerate(particle_list), reverse=True):
      if particle.update():
        particle_list.pop(index)

    for index, particle in sorted(enumerate(mouse_particle_list), reverse=True):
      if particle.update(mos_pos):
        mouse_particle_list.pop(index)

    # drawing particles
    for particle in particle_list + mouse_particle_list:
      particle.draw(particle_surf)

    # shadows
    game_surf.blit(add_shadows(particle_surf, (50, 50, 50)), (0, 0))

    # drawing glow
    for particle in particle_list:
      if particle.glow["size"] >= 1:
        apply_glow(
            game_surf,
            particle.glow["size"] * (particle.current_size / particle.size),
            particle.glow["colour"],
            particle.glow["rings_num"],
            particle.pos,
            mult=1
        )

    screen.blit(pygame.transform.scale_by(game_surf, zoom), (0, 0))
    pygame.display.flip()

    clock.tick(60)

  pygame.quit()
  sys.exit()
